import pawl
from pawl.utils.get_access_token import get_access_token

linkedin = pawl.Linkedin(
    client_id="",  # provide client_id here
    client_secret="",  # provide client_secret here
    redirect_uri="http://localhost:8000",
)

code = get_access_token(linkedin=linkedin)

print("Authorizing...")
linkedin.auth.authorize(code)
print(f"Basic Profile Data: {linkedin.current_user.basic_profile()}")
