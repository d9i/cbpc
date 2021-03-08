import os
import sys

aws_ecr_url = "285585870132.dkr.ecr.us-east-1.amazonaws.com"
profile = "home"

if len(sys.argv) != 3:
    print("Build script usage: python build.py ACTION CONTAINER_TAG")

arg = sys.argv[1]
target = sys.argv[2]

if arg == "build":
    os.system(fr"docker build -t {aws_ecr_url}/{target} .")
elif arg == "push":
    os.system(
        fr"aws ecr get-login-password --region us-east-1 --profile {profile} | docker login --username AWS --password-stdin {aws_ecr_url}/{target}")
    os.system(fr"docker push {aws_ecr_url}/{target}")

elif arg == "run":
    os.system(fr"docker run -it -p 9000:8080 {aws_ecr_url}/{target}:latest")

else:
    print("invalid input")
