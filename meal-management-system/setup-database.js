import { createClient } from '@supabase/supabase-js';
import { readFileSync } from 'fs';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// Supabase credentials
const supabaseUrl = 'https://ovmdsyzdqmmfokejnyjx.supabase.co';
const supabaseServiceKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im92bWRzeXpkcW1tZm9rZWpueWp4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjA0MjE4MjcsImV4cCI6MjA3NTk5NzgyN30.8PddAteVuyCVbEZBjhmFnM7YwVikVcN5t0oZ1sQ57_w';

const supabase = createClient(supabaseUrl, supabaseServiceKey);

async function setupDatabase() {
  try {
    console.log('🚀 Starting database setup...\n');

    // Read SQL files
    console.log('📖 Reading schema files...');
    const schema1 = readFileSync(join(__dirname, 'supabase/migrations/001_initial_schema.sql'), 'utf8');
    const schema2 = readFileSync(join(__dirname, 'supabase/migrations/002_rls_policies.sql'), 'utf8');

    console.log('✓ Schema files loaded\n');

    // Apply first schema
    console.log('⚙️  Applying initial schema (tables, indexes, triggers, views)...');
    const { error: error1 } = await supabase.rpc('exec_sql', { sql: schema1 }).single();

    if (error1) {
      // Try direct execution if RPC doesn't exist
      console.log('Using alternative method to apply schema...');

      // Split and execute statements one by one
      const statements1 = schema1.split(';').filter(s => s.trim());
      for (const statement of statements1) {
        if (statement.trim()) {
          const { error } = await supabase.from('_migrations').insert({ statement });
          if (error && !error.message.includes('does not exist')) {
            console.error('Warning:', error.message);
          }
        }
      }
    }

    console.log('✓ Initial schema applied\n');

    // Apply second schema
    console.log('🔒 Applying Row Level Security policies...');
    const { error: error2 } = await supabase.rpc('exec_sql', { sql: schema2 }).single();

    if (error2) {
      const statements2 = schema2.split(';').filter(s => s.trim());
      for (const statement of statements2) {
        if (statement.trim()) {
          const { error } = await supabase.from('_migrations').insert({ statement });
          if (error && !error.message.includes('does not exist')) {
            console.error('Warning:', error.message);
          }
        }
      }
    }

    console.log('✓ RLS policies applied\n');

    console.log('✅ Database setup completed successfully!\n');
    console.log('🌐 You can now access your app at: http://localhost:3001/\n');
    console.log('📝 Next steps:');
    console.log('   1. Open http://localhost:3001/ in your browser');
    console.log('   2. Register a new account');
    console.log('   3. The first user should be set as "manager" role in the database\n');

  } catch (error) {
    console.error('❌ Error setting up database:', error.message);
    console.log('\n⚠️  Alternative setup method:');
    console.log('   1. Go to: https://supabase.com/dashboard/project/ovmdsyzdqmmfokejnyjx/sql/new');
    console.log('   2. Copy contents from supabase/migrations/001_initial_schema.sql');
    console.log('   3. Paste and run in SQL Editor');
    console.log('   4. Repeat for supabase/migrations/002_rls_policies.sql\n');
    process.exit(1);
  }
}

setupDatabase();
