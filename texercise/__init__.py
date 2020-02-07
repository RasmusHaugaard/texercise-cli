import os
import zipfile
import tempfile
import time
from pathlib import Path

import requests

base_url = 'http://texercise.rasmushaugaard.dk'


def load_config(fp: Path = None):
    if fp is not None:
        try:
            with fp.open() as f:
                course, email, token = [l.strip() for l in f.readlines()]
        except Exception as e:
            print("Could not read .texercise file")
            raise e
        return course, email, token

    folder = Path()
    fp = folder / ".texercise"
    if fp.exists():
        return "course", load_config(fp)
    fp = folder.parent / ".texercise"
    if fp.exists():
        return "exercise", load_config(fp)
    return None, (None, None, None)


def zipdir(dir: Path):
    tmp = tempfile.mktemp(prefix="texercise-", suffix=".zip")
    zipf = zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED)
    for root, dirs, files in os.walk(str(dir.absolute())):
        for file in files:
            zipf.write(os.path.join(root, file))
    zipf.close()
    return tmp


def main():
    z = zipdir()
    r = requests.post(
        url='{}/upload'.format(base_url),
        files={'archive': open(z, 'rb')},
    )
    response_data = r.json()
    print(response_data)
    job_id = response_data['data']['job_id']
    print(job_id)
    return job_id


if __name__ == '__main__':
    job_id = main()
    while True:
        r = requests.get("{}/jobs/{}".format(base_url, job_id))
        data = r.json()['data']
        job_status = data['job_status']
        if job_status == 'queued':
            print("queued")
        elif job_status == 'started':
            print("Currently checking your solution")
        else:
            print("job_status", job_status)
            break
        time.sleep(1)
    print(data['job_result'])
