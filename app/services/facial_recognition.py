import cv2
import mediapipe as mp
import numpy as np
from typing import Optional, List, Tuple
import os

from app.models.facial_encoding import FacialEncoding
from app.utils.logging import logger

class FacialRecognitionService:
    def __init__(self):
        # Stage 2: Face Mesh Engine (468 landmarks)
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            static_image_mode=True,
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.7
        )
        
        # Stage 1: Face Detection Pre-filter (Strict Liveness/Object check)
        self.mp_face_detection = mp.solutions.face_detection
        self.face_detection = self.mp_face_detection.FaceDetection(
            model_selection=1, # Long-range model for kiosk distance
            min_detection_confidence=0.85 # High confidence required to avoid hands/spoofs
        )

    def extract_face_features(self, image: np.ndarray) -> Optional[np.ndarray]:
        """
        Extract 468 facial landmarks with 3D Alignment and Detection filtering.
        """
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # --- Stage 1: Detection Confidence Pre-filter ---
        # This prevents hands, silhouettes, or non-face objects from being processed.
        detection_results = self.face_detection.process(rgb_image)
        if not detection_results.detections:
            logger.debug("Security: No legitimate face detected (REJECTED)")
            return None
            
        face_conf = detection_results.detections[0].score[0]
        if face_conf < 0.85:
            logger.debug(f"Security: Face detection confidence too low ({face_conf:.2f}), REJECTED.")
            return None

        # --- Stage 2: Face Mesh Landmark Extraction ---
        mesh_results = self.face_mesh.process(rgb_image)
        if not mesh_results.multi_face_landmarks:
            logger.debug("Security: FaceMesh failed to acquire biometric map.")
            return None

        face_landmarks = mesh_results.multi_face_landmarks[0]
        landmarks = face_landmarks.landmark

        # Get key anchors for spatial alignment
        nose = landmarks[4]
        r_eye = landmarks[33] 
        l_eye = landmarks[263]

        # --- Stage 3: 3D Roll Alignment (Canonical Face Projection) ---
        # Calculate angle to make eyes perfectly horizontal (normalizes head tilt)
        dy = l_eye.y - r_eye.y
        dx = l_eye.x - r_eye.x
        angle = np.arctan2(dy, dx)
        cos_tr = np.cos(-angle)
        sin_tr = np.sin(-angle)

        # Scale normalization (Inter-pupillary distance)
        eye_dist = np.sqrt(dx**2 + dy**2)
        if eye_dist < 1e-6:
            eye_dist = 0.1

        feature_vector = []
        for lm in landmarks:
            # 1. Translation: Move nose to origin (0,0,0)
            tx = (lm.x - nose.x)
            ty = (lm.y - nose.y)
            tz = (lm.z - nose.z)
            
            # 2. Rotation: Align eyes to horizontal axis
            nx = (tx * cos_tr - ty * sin_tr) / eye_dist
            ny = (tx * sin_tr + ty * cos_tr) / eye_dist
            nz = tz / eye_dist
            
            feature_vector.extend([nx, ny, nz])

        return np.array(feature_vector, dtype=np.float64)

    def process_image(self, file_content: bytes) -> Optional[np.ndarray]:
        """Decode and extract aligned biometric features."""
        nparr = np.frombuffer(file_content, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if image is None:
            return None
        return self.extract_face_features(image)

    async def load_known_encodings(self) -> Tuple[List[np.ndarray], List[int]]:
        """Load and decode biometric database."""
        encodings_db = await FacialEncoding.all()
        known_encodings = []
        known_client_ids = []
        
        for enc in encodings_db:
            arr = np.frombuffer(enc.encoding_data, dtype=np.float64)
            known_encodings.append(arr)
            known_client_ids.append(enc.client_id)
            
        return known_encodings, known_client_ids

    async def identify_client(self, file_content: bytes) -> Optional[int]:
        """
        Identify client with High Sensitivity front-facing alignment.
        """
        unknown_features = self.process_image(file_content)
        if unknown_features is None:
            return None

        known_encodings, known_client_ids = await self.load_known_encodings()
        if not known_encodings:
            return None

        best_match_id = None
        min_dist = 99.9 
        closest_dist = 99.9 

        for i, known_encoding in enumerate(known_encodings):
            if len(unknown_features) != len(known_encoding):
                continue

            # Standard Euclidean Distance on aligned mesh
            dist = np.linalg.norm(unknown_features - known_encoding)
            
            if dist < closest_dist:
                closest_dist = dist

            # NEW SECURITY THRESHOLD: 2.3 (Highly Strict)
            # Alignment makes variations smaller, so we can be much more strict.
            if dist < 2.3: 
                if dist < min_dist:
                    min_dist = dist
                    best_match_id = known_client_ids[i]

        if best_match_id:
            logger.debug(f"FaceMatch: SECURE MATCH! ID {best_match_id} | Dist {min_dist:.4f}")
        else:
            logger.debug(f"FaceMatch: NO MATCH. Strict-Closest: {closest_dist:.4f}")

        return best_match_id

    async def register_face(self, client_id: int, file_content: bytes):
        """Register face with front-facing canonical alignment."""
        features = self.process_image(file_content)
        if features is None:
            raise ValueError("No se pudo detectar un rostro claro. Centra tu cara y mejora la luz.")

        await FacialEncoding.filter(client_id=client_id).delete()
        
        await FacialEncoding.create(
            client_id=client_id,
            encoding_data=features.tobytes()
        )
        
        logger.info(f"Register: Aligned biometric enrollment complete for client {client_id}")
        return True
