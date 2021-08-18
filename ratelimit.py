import requests 

#check and print current ratelimit if exists
r = requests.head(url="https://discord.com/api/v1") 
try: 
	print(f"Rate limit {int(r.headers['Retry-After']) / 60} minutes left") 
except: 
	print("No rate limit")