import docker
from docker.tls import TLSConfig

with docker.DockerClient(
    base_url="unix:///var/run/docker.sock", tls=TLSConfig(verify=False)
) as client:
    command = """
    export GITHUB_AUTH_TOKEN={} &&
    scorecard --repo={https://github.com/ossf/scorecard}
    """

    repo_url = "https://github.com/ossf/scorecard"
    command0 = f"scorecard --repo={repo_url}"

    res = client.containers.run("gcr.io/openssf/scorecard:stable", command0)

    print(res)
print("DONE")

"""
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo chown "$(id -u)":docker /var/run/docker.sock


sudo apt-get update &&
sudo apt-get install docker.io &&
sudo service docker start &&
sudo usermod -aG docker $USER &&
newgrp docker &&
sudo service docker restart
"""
