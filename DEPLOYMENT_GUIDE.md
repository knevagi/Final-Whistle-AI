# Supabase Database Setup Instructions

## 1. Create Supabase Project
- Go to https://supabase.com
- Sign up/Login
- Create new project
- Choose a region close to your users
- Set a strong database password

## 2. Run Database Schema
- Go to SQL Editor in your Supabase dashboard
- Copy and paste the contents of `database/schema.sql`
- Click "Run" to execute the schema

## 3. Get Your Credentials
- Go to Settings → API
- Copy your Project URL and anon/public key
- Use these in your Railway environment variables

## 4. Enable Storage
- Go to Storage in your Supabase dashboard
- The schema already creates the `article-images` bucket
- Verify it exists and is public

## 5. Test Connection
- Use the API test endpoints to verify everything works
- Check that tables are created correctly
