import glob
import requests

import parameters

post_url = 'https://kapi.kakao.com/v1/vision/multitag/generate'

headers = {'Authorization': f'KakaoAK {parameters.restapi_key}'}

for image_path in parameters.images_paths:

    images = glob.glob(image_path + "/*.*")

    labels = []

    for idx, img in enumerate(images):

        print(idx+1, ':', img)     

        # read the image
        files = {'file': open(img, "rb")}

        # http POST
        response = requests.post(
        post_url, headers=headers, files=files
        )

        # raise a error if status code is not '200 OK'
        response.raise_for_status()
        status_code = response.status_code
        print('status code:', status_code)

        analysis = response.json()
        print(analysis)

        label_kr = analysis['result']['label_kr']

        for label in label_kr:
            if label in labels: 
                continue
            labels.append(label)

    print('전체 라벨 :', labels)

    with open(f'labels.txt', 'a') as file:
        file.write(f'<{image_path}>\n')
        file.write(' '.join(labels)+'\n')

    