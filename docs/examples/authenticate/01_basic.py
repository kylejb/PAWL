import pawl

linkedin = pawl.Linkedin(
    client_id="",  # provide client_id here
    client_secret="",  # provide client_secret here
    redirect_uri="http://localhost:8000",
)

url = linkedin.auth.url()
print("click here", url)

code = input("Enter code: ")

print("Authorizing...")
print(linkedin.auth.authorize(code))
print(f"Basic Profile Data: {linkedin.current_user.basic_profile()}")
