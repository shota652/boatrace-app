from supabase import create_client, Client

url = "https://dhmtiglgbmrsoovgkslg.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRobXRpZ2xnYm1yc29vdmdrc2xnIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDc0NjM0NzksImV4cCI6MjA2MzAzOTQ3OX0.nH5amkfjl4JFFgUa7ZSojlvBa_m0IpIznCIYQ3Ol8n8"

supabase: Client = create_client(url, key)