import { createClient } from '@supabase/supabase-js';
import { readFileSync } from 'fs';

const supabaseUrl = 'https://ovmdsyzdqmmfokejnyjx.supabase.co';
const supabaseKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im92bWRzeXpkcW1tZm9rZWpueWp4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjA0MjE4MjcsImV4cCI6MjA3NTk5NzgyN30.8PddAteVuyCVbEZBjhmFnM7YwVikVcN5t0oZ1sQ57_w';

const supabase = createClient(supabaseUrl, supabaseKey);

console.log('🚀 Setting up database...\n');

// Read schema files
const schema1 = readFileSync('./supabase/migrations/001_initial_schema.sql', 'utf8');
const schema2 = readFileSync('./supabase/migrations/002_rls_policies.sql', 'utf8');

console.log('📝 Schema files loaded');
console.log('⚙️  Applying to Supabase...\n');

// Function to execute SQL via REST API
async function executeSQL(sql) {
  const response = await fetch(`${supabaseUrl}/rest/v1/rpc/exec_sql`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'apikey': supabaseKey,
      'Authorization': `Bearer ${supabaseKey}`
    },
    body: JSON.stringify({ query: sql })
  });

  return response;
}

// Try to apply schemas
try {
  console.log('Step 1: Applying initial schema...');
  await executeSQL(schema1);
  console.log('✓ Initial schema applied\n');

  console.log('Step 2: Applying security policies...');
  await executeSQL(schema2);
  console.log('✓ Security policies applied\n');

  console.log('✅ SUCCESS! Database is ready!\n');
  console.log('🌐 Open your app: http://localhost:3001/\n');
} catch (error) {
  console.log('⚠️  Automated setup not available.\n');
  console.log('Please use manual setup:\n');
  console.log('1. Go to: https://supabase.com/dashboard/project/ovmdsyzdqmmfokejnyjx/sql/new');
  console.log('2. Copy the file: supabase/migrations/001_initial_schema.sql');
  console.log('3. Paste and click RUN');
  console.log('4. Copy the file: supabase/migrations/002_rls_policies.sql');
  console.log('5. Paste and click RUN\n');
}
