import glob
import requests
import os
import shutil
import csv

import parameters


def request_kakao_vision_api(img):
    post_url = 'https://kapi.kakao.com/v1/vision/multitag/generate'

    headers = {'Authorization': f'KakaoAK {parameters.restapi_key}'}

    print(f'\n\n******* Request Kakao Vision API... ==> IMAGE: {img}')    

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
    print(label_kr)


    # analysis results dict
    human_or_not = 0
    outdoor_or_not = 0
    food_or_not = 0
    building_or_not = 0
    animal_or_not = 0


    # 사람
    if ('사람' in label_kr) or ('여러사람' in label_kr) or ('한사람' in label_kr) or ('여성' in label_kr) or ('남성' in label_kr) or ('아기' in label_kr):
        human_or_not = 1

    # 실외/실내
    if ('실외' in label_kr) or ('산' in label_kr) or ('하늘' in label_kr) or ('해변' in label_kr):
        outdoor_or_not = 1


    # 음식
    if ('음식' in label_kr):
        food_or_not = 1

    # 건물
    if ('건물' in label_kr):
        building_or_not = 1
    
    # 동물
    if ('동물' in label_kr) or ('개' in label_kr) or ('포유류' in label_kr) or ('고양이' in label_kr):
        animal_or_not = 1


    results = {
        'tag_list': label_kr,
        'human_or_not': human_or_not,
        'outdoor_or_not': outdoor_or_not,
        'food_or_not': food_or_not,
        'building_or_not': building_or_not,
        'animal_or_not': animal_or_not
    }

    print(results)
    print(f'\n\n******* END...\n\n')

    return results



if __name__ == "__main__":

    for images_path in parameters.images_paths:

        images = sorted(glob.glob(images_path + "/*.jpg"))

        csv_filename = f'results/results_[{images_path}].csv'
        new_csv_filename = f'results/new_results_[{images_path}].csv'

        # open the result file
        in_f = open(csv_filename, 'r', newline='', encoding='utf-8')
        out_f = open(new_csv_filename, 'a+', newline='', encoding='utf-8')

        in_reader = csv.reader(in_f)
        out_reader = csv.reader(out_f)
        writer = csv.writer(out_f)

        # write colname in a new csv result file
        # api 멈췄을 때 다시 돌릴 때는 colname 적을 필요 없음
        existed_rows = [row for row in out_reader]
        print('existed_rows===>', existed_rows)
        if len(existed_rows) == 0:
            colname = ['num', 'filename', 'shortcode', 'date_utc', 'likes_num', 'text', 'comments', 
                        'comments_num', 'hashtags', 'hashtags_num', 'gps', 'gps_detail', 'tag_list', 
                        'human_or_not', 'outdoor_or_not', 'food_or_not', 'building_or_not', 'animal_or_not']
            writer.writerow(colname)


        for idx, img in enumerate(images):

            filename = img.split('/')[-1]

            # request kakao vision api
            vision_results = request_kakao_vision_api(img)

            # find the location of vision_results in the csv file
            for row in in_reader:
                # print('row', row, '\n\n\n')
                # print('row[1]', row[1])
                # print('filename', filename)
                if row[1] == filename:
                    row.append(vision_results['tag_list'])
                    row.append(vision_results['human_or_not'])
                    row.append(vision_results['outdoor_or_not'])
                    row.append(vision_results['food_or_not'])
                    row.append(vision_results['building_or_not'])
                    row.append(vision_results['animal_or_not'])

                    writer.writerow(row)
                    break

                

                    
            if not os.path.exists(images_path + '/completed_img/'): # make results directory
                os.makedirs(images_path + '/completed_img/')


            # move this image to the completed folder
            shutil.move(img, images_path + '/completed_img/' + filename)

        in_f.close()
        out_f.close()
            

    

    