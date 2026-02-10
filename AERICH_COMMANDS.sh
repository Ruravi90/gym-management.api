#!/bin/bash
# Aerich Migration Commands Reference
# Common commands for managing database migrations with Aerich

echo "================================"
echo "  Aerich Migration Commands"
echo "================================"
echo ""

echo "📝 VIEWING MIGRATIONS:"
echo "  aerich history                    # Show all migrations"
echo ""

echo "✨ CREATING NEW MIGRATIONS:"
echo "  aerich migrate --name add_field   # Create migration for model changes"
echo ""

echo "📤 APPLYING MIGRATIONS:"
echo "  aerich upgrade                    # Apply all pending migrations"
echo ""

echo "⏮️  ROLLING BACK:"
echo "  aerich downgrade                  # Rollback last migration"
echo "  aerich downgrade --num 2          # Rollback last 2 migrations"
echo ""

echo "🔍 CHECKING STATUS:"
echo "  aerich heads                      # Show latest migration"
echo "  aerich show                       # Show migration details"
echo ""

echo "🚀 COMPLETE WORKFLOW:"
echo "  1. Edit your models (app/models/)"
echo "  2. aerich migrate --name 'description'"
echo "  3. Review generated migration file"
echo "  4. aerich upgrade"
echo ""

echo "💡 TIPS:"
echo "  - Always review migrations before applying"
echo "  - Use descriptive names for migrations"
echo "  - Keep backups of production database"
echo "  - Test migrations on staging first"
echo ""

echo "📚 DOCUMENTATION:"
echo "  https://github.com/tortoise/aerich"
echo ""
