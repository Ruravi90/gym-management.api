import math
from datetime import date, datetime, timedelta
from typing import List, Optional
from app.models.client import Client
from app.models.gamification import (
    XpLog, AchievementDefinition, ClientAchievement,
    WeeklyChallenge, ClientChallenge,
    ActionType, CriteriaType,
)


class GamificationService:

    @staticmethod
    def calculate_level(xp: int) -> int:
        if xp < 0:
            return 1
        return math.floor(math.sqrt(xp / 100)) + 1

    @staticmethod
    def xp_for_level(level: int) -> int:
        if level <= 1:
            return 0
        return (level - 1) ** 2 * 100

    @staticmethod
    def xp_for_next_level(current_level: int) -> int:
        return GamificationService.xp_for_level(current_level + 1)

    @staticmethod
    def xp_progress_percent(xp: int, current_level: int) -> float:
        current_level_xp = GamificationService.xp_for_level(current_level)
        next_level_xp = GamificationService.xp_for_next_level(current_level)
        if next_level_xp <= current_level_xp:
            return 100.0
        progress = (xp - current_level_xp) / (next_level_xp - current_level_xp)
        return min(round(progress * 100, 1), 100.0)

    @staticmethod
    def streak_multiplier(current_streak: int) -> int:
        if current_streak >= 30:
            return 2
        if current_streak >= 7:
            return 2
        return 1

    async def award_xp(
        self,
        client_id: int,
        action_type: str,
        base_amount: int,
        description: str,
    ) -> dict:
        client = await Client.get_or_none(id=client_id)
        if not client:
            raise ValueError(f"Client {client_id} not found")

        multiplier = self.streak_multiplier(client.current_streak)
        final_amount = base_amount * multiplier

        if multiplier > 1:
            description = f"{description} (x{multiplier} racha)"

        await XpLog.create(
            client_id=client_id,
            action_type=action_type,
            xp_amount=final_amount,
            description=description,
        )

        old_level = client.level
        client.xp += final_amount
        client.level = self.calculate_level(client.xp)
        client.last_activity_date = date.today()
        await client.save()

        leveled_up = client.level > old_level

        await self._check_achievements(client)
        await self.evaluate_challenges(client_id)

        return {
            "xp_gained": final_amount,
            "new_xp_total": client.xp,
            "old_level": old_level,
            "new_level": client.level,
            "leveled_up": leveled_up,
            "description": description,
        }

    async def update_streak(self, client_id: int) -> dict:
        client = await Client.get_or_none(id=client_id)
        if not client:
            raise ValueError(f"Client {client_id} not found")

        today = date.today()
        old_streak = client.current_streak

        if client.last_activity_date == today:
            return {
                "current_streak": client.current_streak,
                "longest_streak": client.longest_streak,
                "last_activity_date": client.last_activity_date,
                "streak_updated": False,
            }

        if client.last_activity_date == today - timedelta(days=1):
            client.current_streak += 1
        elif client.last_activity_date is None:
            client.current_streak = 1
        else:
            client.current_streak = 1

        if client.current_streak > client.longest_streak:
            client.longest_streak = client.current_streak

        await client.save()

        streak_changed = client.current_streak != old_streak
        if streak_changed:
            if client.current_streak == 7:
                await self.award_xp(
                    client_id, "streak_bonus", 50, "Bonus: 7 días de racha"
                )
            elif client.current_streak == 30:
                await self.award_xp(
                    client_id, "streak_bonus", 200, "Bonus: 30 días de racha"
                )

        return {
            "current_streak": client.current_streak,
            "longest_streak": client.longest_streak,
            "last_activity_date": client.last_activity_date,
            "streak_updated": streak_changed,
        }

    async def get_progress_summary(self, client_id: int) -> dict:
        client = await Client.get_or_none(id=client_id)
        if not client:
            raise ValueError(f"Client {client_id} not found")

        return {
            "level": client.level,
            "xp": client.xp,
            "xp_for_next_level": self.xp_for_next_level(client.level),
            "xp_progress_percent": self.xp_progress_percent(client.xp, client.level),
            "current_streak": client.current_streak,
            "longest_streak": client.longest_streak,
        }

    async def get_xp_history(
        self, client_id: int, limit: int = 20, offset: int = 0
    ) -> List[dict]:
        logs = (
            await XpLog.filter(client_id=client_id)
            .order_by("-created_at")
            .offset(offset)
            .limit(limit)
        )
        return [
            {
                "id": log.id,
                "action_type": log.action_type,
                "xp_amount": log.xp_amount,
                "description": log.description,
                "created_at": log.created_at,
            }
            for log in logs
        ]

    async def get_achievements_with_status(self, client_id: int) -> List[dict]:
        definitions = await AchievementDefinition.filter(is_active=True)
        earned = await ClientAchievement.filter(client_id=client_id).prefetch_related(
            "achievement"
        )
        earned_map = {
            ca.achievement.key: ca for ca in earned
        }

        client = await Client.get_or_none(id=client_id)
        stats = await self._get_client_stats(client_id)

        result = []
        for defn in definitions:
            is_earned = defn.key in earned_map
            earned_date = (
                earned_map[defn.key].earned_date if is_earned else None
            )
            progress = self._get_progress_for_criteria(defn, stats, client)

            result.append(
                {
                    "key": defn.key,
                    "name": defn.name,
                    "description": defn.description,
                    "icon": defn.icon,
                    "xp_reward": defn.xp_reward,
                    "earned": is_earned,
                    "earned_date": earned_date,
                    "progress": min(progress, defn.criteria_value),
                    "target": defn.criteria_value,
                }
            )

        return result

    async def _get_client_stats(self, client_id: int) -> dict:
        from app.models.attendance import Attendance
        from app.models.kaizen import KaizenLog
        from app.models.routine import WorkoutSession, SetLog
        from app.models.measurement import BodyMeasurement

        checkins = await Attendance.filter(client_id=client_id).count()
        kaizen_victories = (
            await KaizenLog.filter(
                habit__client_id=client_id, status="victory"
            ).count()
        )
        workouts = (
            await WorkoutSession.filter(
                client_id=client_id, status="completed"
            ).count()
        )
        sets = await SetLog.filter(session__client_id=client_id).count()
        measurements = await BodyMeasurement.filter(client_id=client_id).count()

        return {
            "checkins_total": checkins,
            "kaizen_victories": kaizen_victories,
            "workouts_completed": workouts,
            "sets_total": sets,
            "measurements_total": measurements,
        }

    def _get_progress_for_criteria(
        self, defn: AchievementDefinition, stats: dict, client: Client
    ) -> int:
        mapping = {
            CriteriaType.CHECKINS_TOTAL: "checkins_total",
            CriteriaType.STREAK_DAYS: None,
            CriteriaType.KAIZEN_VICTORIES: "kaizen_victories",
            CriteriaType.WORKOUTS_COMPLETED: "workouts_completed",
            CriteriaType.SETS_TOTAL: "sets_total",
            CriteriaType.MEASUREMENTS_TOTAL: "measurements_total",
            CriteriaType.XP_TOTAL: None,
            CriteriaType.LEVEL_REACHED: None,
        }

        if defn.criteria_type == CriteriaType.STREAK_DAYS:
            return client.longest_streak
        if defn.criteria_type == CriteriaType.XP_TOTAL:
            return client.xp
        if defn.criteria_type == CriteriaType.LEVEL_REACHED:
            return client.level

        stat_key = mapping.get(defn.criteria_type)
        if stat_key:
            return stats.get(stat_key, 0)
        return 0

    async def _check_achievements(self, client: Client):
        definitions = await AchievementDefinition.filter(is_active=True)
        earned = await ClientAchievement.filter(client_id=client.id).prefetch_related(
            "achievement"
        )
        earned_keys = {ca.achievement.key for ca in earned}

        stats = await self._get_client_stats(client.id)

        for defn in definitions:
            if defn.key in earned_keys:
                continue

            progress = self._get_progress_for_criteria(defn, stats, client)
            if progress >= defn.criteria_value:
                await ClientAchievement.create(
                    client_id=client.id, achievement_id=defn.id
                )
                await self.award_xp(
                    client.id,
                    "achievement_unlocked",
                    defn.xp_reward,
                    f"Logro desbloqueado: {defn.name}",
                )

    # =========================================================
    # Weekly Challenges
    # =========================================================

    async def get_active_challenges(self, client_id: int) -> List[dict]:
        today = date.today()
        challenges = await WeeklyChallenge.filter(
            is_active=True,
            start_date__lte=today,
            end_date__gte=today,
        )

        client_progress = await ClientChallenge.filter(
            client_id=client_id,
            challenge_id__in=[c.id for c in challenges],
        )
        progress_map = {cp.challenge_id: cp for cp in client_progress}

        result = []
        for ch in challenges:
            cp = progress_map.get(ch.id)
            current = cp.current_progress if cp else 0
            completed = cp.completed if cp else False
            completed_at = cp.completed_at if cp else None
            pct = min(round((current / ch.criteria_value) * 100, 1), 100.0) if ch.criteria_value > 0 else 0.0

            result.append({
                "id": ch.id,
                "title": ch.title,
                "description": ch.description,
                "xp_reward": ch.xp_reward,
                "criteria_type": ch.criteria_type,
                "criteria_value": ch.criteria_value,
                "start_date": ch.start_date,
                "end_date": ch.end_date,
                "current_progress": current,
                "completed": completed,
                "completed_at": completed_at,
                "progress_percent": pct,
            })

        return result

    async def evaluate_challenges(self, client_id: int) -> List[dict]:
        today = date.today()
        active_challenges = await WeeklyChallenge.filter(
            is_active=True,
            start_date__lte=today,
            end_date__gte=today,
        )

        if not active_challenges:
            return []

        client = await Client.get_or_none(id=client_id)
        if not client:
            return []

        stats = await self._get_client_stats(client_id)
        newly_completed = []

        for ch in active_challenges:
            progress = self._get_challenge_progress(ch, stats, client)

            cp = await ClientChallenge.get_or_none(
                client_id=client_id, challenge_id=ch.id
            )

            if cp is None:
                cp = await ClientChallenge.create(
                    client_id=client_id,
                    challenge_id=ch.id,
                    current_progress=progress,
                    completed=progress >= ch.criteria_value,
                    completed_at=datetime.now() if progress >= ch.criteria_value else None,
                )
                if progress >= ch.criteria_value:
                    await self.award_xp(
                        client_id,
                        "streak_bonus",
                        ch.xp_reward,
                        f"Reto completado: {ch.title}",
                    )
                    newly_completed.append({
                        "id": ch.id,
                        "title": ch.title,
                        "xp_reward": ch.xp_reward,
                    })
            elif not cp.completed:
                cp.current_progress = progress
                if progress >= ch.criteria_value:
                    cp.completed = True
                    cp.completed_at = datetime.now()
                    await self.award_xp(
                        client_id,
                        "streak_bonus",
                        ch.xp_reward,
                        f"Reto completado: {ch.title}",
                    )
                    newly_completed.append({
                        "id": ch.id,
                        "title": ch.title,
                        "xp_reward": ch.xp_reward,
                    })
                await cp.save()

        return newly_completed

    def _get_challenge_progress(
        self, ch: WeeklyChallenge, stats: dict, client: Client
    ) -> int:
        mapping = {
            CriteriaType.CHECKINS_TOTAL: "checkins_total",
            CriteriaType.KAIZEN_VICTORIES: "kaizen_victories",
            CriteriaType.WORKOUTS_COMPLETED: "workouts_completed",
            CriteriaType.SETS_TOTAL: "sets_total",
            CriteriaType.MEASUREMENTS_TOTAL: "measurements_total",
        }

        if ch.criteria_type == CriteriaType.STREAK_DAYS:
            return client.current_streak
        if ch.criteria_type == CriteriaType.XP_TOTAL:
            return client.xp
        if ch.criteria_type == CriteriaType.LEVEL_REACHED:
            return client.level

        stat_key = mapping.get(ch.criteria_type)
        if stat_key:
            return stats.get(stat_key, 0)
        return 0
