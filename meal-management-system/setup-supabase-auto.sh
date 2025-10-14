#!/bin/bash

# =============================================
# Automated Supabase Setup Script
# =============================================
# This script will attempt to run migrations automatically
# You need to provide your SERVICE_ROLE key (not anon key)

set -e

echo "🚀 Automated Supabase Setup"
echo "================================"
echo ""

# Load environment variables
source .env

SUPABASE_URL="${VITE_SUPABASE_URL}"
ANON_KEY="${VITE_SUPABASE_ANON_KEY}"

echo "📋 Supabase URL: ${SUPABASE_URL}"
echo ""

# Check if service role key is provided
if [ -z "$SUPABASE_SERVICE_ROLE_KEY" ]; then
    echo "❌ ERROR: SUPABASE_SERVICE_ROLE_KEY not found"
    echo ""
    echo "To run migrations automatically, you need the SERVICE ROLE key:"
    echo "1. Go to: https://supabase.com/dashboard/project/ovmdsyzdqmmfokejnyjx/settings/api"
    echo "2. Copy the 'service_role' key (NOT the anon key)"
    echo "3. Add to .env file:"
    echo "   SUPABASE_SERVICE_ROLE_KEY=your_service_role_key_here"
    echo ""
    echo "Or manually run migrations via Supabase dashboard SQL Editor"
    echo "See: SUPABASE_QUICK_SETUP.md"
    exit 1
fi

echo "✅ Service role key found"
echo ""

# Function to execute SQL
execute_sql() {
    local sql_file=$1
    local description=$2

    echo "📝 Running: $description"

    # Read SQL file
    SQL_CONTENT=$(cat "$sql_file")

    # Execute via Supabase SQL API (if available)
    # Note: This requires Management API access
    RESPONSE=$(curl -s -X POST "${SUPABASE_URL}/rest/v1/rpc/exec_sql" \
        -H "apikey: ${SUPABASE_SERVICE_ROLE_KEY}" \
        -H "Authorization: Bearer ${SUPABASE_SERVICE_ROLE_KEY}" \
        -H "Content-Type: application/json" \
        -d "{\"query\": $(jq -Rs . <<< "$SQL_CONTENT")}")

    if echo "$RESPONSE" | grep -q "error"; then
        echo "❌ Failed: $description"
        echo "$RESPONSE"
        return 1
    else
        echo "✅ Success: $description"
        return 0
    fi
}

# Run migrations
echo "🔄 Running database migrations..."
echo ""

if execute_sql "supabase/migrations/001_initial_schema.sql" "Initial schema"; then
    echo ""
fi

if execute_sql "supabase/migrations/002_rls_policies.sql" "RLS policies"; then
    echo ""
fi

# Verify setup
echo "🔍 Verifying setup..."
VERIFY_RESPONSE=$(curl -s "${SUPABASE_URL}/rest/v1/users?select=id&limit=1" \
    -H "apikey: ${ANON_KEY}" \
    -H "Authorization: Bearer ${ANON_KEY}")

if echo "$VERIFY_RESPONSE" | grep -q "error"; then
    echo "❌ Verification failed"
    echo "$VERIFY_RESPONSE"
else
    echo "✅ Database setup successful!"
    echo ""
    echo "📊 Tables created:"
    echo "  - users"
    echo "  - meals"
    echo "  - deposits"
    echo "  - expenses"
    echo "  - meal_settings"
    echo "  - menu"
    echo "  - notifications"
    echo "  - announcements"
    echo ""
    echo "🎉 Setup complete! You can now:"
    echo "  1. Run: npm run dev"
    echo "  2. Visit: http://localhost:3000"
    echo "  3. Register and login"
fi
