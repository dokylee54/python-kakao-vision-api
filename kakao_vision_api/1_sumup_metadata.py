import parameters
import glob
import json
import csv
import os

'''
colname = ['num', 'filename', 'shortcode', 'date_utc', 'likes_num', 'text', 'comments', 
                'comments_num', 'hashtags', 'hashtags_num', 'gps', 'gps_detail', 'tag_list', 
                'human_or_not', 'outdoor_or_not', 'food_or_not', 'building_or_not', 'animal_or_not']

img filename => {yyyy-mm-dd_hh-mm-ss}!{shortcode}.jpg
img metadata filename => {yyyy-mm-dd_hh-mm-ss}!{shortcode}.txt
img gps filename => {yyyy-mm-dd_hh-mm-ss}!{shortcode}_location.txt
img comments filename => {yyyy-mm-dd_hh-mm-ss}!{shortcode}_comments.json
'''

if __name__ == "__main__":

    for images_path in parameters.images_paths:

        images = sorted(glob.glob(images_path + "/*.*"))

        len_images = len(images)

        print(f'몇 개의 파일 = {len_images}')

        # make a result csv file & write colname

        if not os.path.exists('results'): # make results directory
            os.makedirs('results')

        csv_filename = f'results/results_[{images_path}].csv'
        colname = ['num', 'filename', 'shortcode', 'date_utc', 'likes_num', 'text', 'comments', 
                'comments_num', 'hashtags', 'hashtags_num', 'gps', 'gps_detail', 'tag_list', 
                'human_or_not', 'outdoor_or_not', 'food_or_not', 'building_or_not', 'animal_or_not']

        with open(csv_filename, 'w', newline='', encoding='utf-8') as f:    
            writer = csv.writer(f)
            writer.writerow(colname) # write column names

        # img num
        img_num = 1

        img_data_sum = {}
        img_metadata = {'jpg_filename': [], 'date_utc': '', 'likes_num': 0, 'body_text': '', 'comments': {}, 
                        'comments_num': 0, 'hashtags': [], 'hashtags_num': 0, 'gps': '', 'gps_detail': ''}

        print(img_metadata)

        # shortcode
        shortcode = '' # if it is the first image

        for idx, onefile in enumerate(images):

            filename = onefile.split('/')[-1]
            print(f'{images_path} 폴더의 {filename} 파일')

            tmp_shortcode = filename.split('!')[1][:11]

            print(f'tmp_shortcode는 {tmp_shortcode}')

            # meet new posting data
            if tmp_shortcode not in img_data_sum:

                print(f'새로운 shortcode 등장!!')
                
                # if it is the first image, there is no accumulated metadata
                if shortcode == '':
                    print('처음 돌리기~~~')
                    print(f'이전 shortcode={shortcode}')
                    shortcode = tmp_shortcode
                    img_data_sum[shortcode] = img_metadata
                    

                else:
                    print('다음 포스팅으로~~~')
                    print(f'이전 shortcode={shortcode}')

                    # write accumulated metadata into csv file
                    # open file
                    with open(csv_filename, 'a', newline='', encoding='utf-8') as f: 
                        
                        writer = csv.writer(f)

                        ## make rowlist by using img_metadata
                        rowlist = []

                        imgs_len_in_posting = len(img_data_sum[shortcode]['jpg_filename'])
                        print(f'포스팅의 사진은 몇개 = {imgs_len_in_posting}')

                        for i in range(imgs_len_in_posting):

                            print(f'** img_num = {img_num}')

                            rowlist.append([
                                img_num,
                                img_data_sum[shortcode]['jpg_filename'][i],
                                shortcode,
                                img_data_sum[shortcode]['date_utc'], 
                                int(img_data_sum[shortcode]['likes_num']), 
                                img_data_sum[shortcode]['body_text'],
                                str(img_data_sum[shortcode]['comments']),
                                int(img_data_sum[shortcode]['comments_num']),
                                str(img_data_sum[shortcode]['hashtags']),
                                int(img_data_sum[shortcode]['hashtags_num']),
                                img_data_sum[shortcode]['gps'],
                                img_data_sum[shortcode]['gps_detail']
                            ])

                            img_num += 1

                        print(f'뭘 쓸꺼냐면 : {rowlist}')

                        ## write one row
                        writer.writerows(rowlist)


                    img_data_sum = {}
                    img_metadata = {'jpg_filename': [], 'date_utc': '', 'likes_num': 0, 'body_text': '', 'comments': {}, 
                                    'comments_num': 0, 'hashtags': [], 'hashtags_num': 0, 'gps': '', 'gps_detail': ''}

                    shortcode = tmp_shortcode
                    img_data_sum[shortcode] = img_metadata

                

            # determine a type of current file
            file_extention = filename.split('.')[-1]


            # ignore extention '.xz'
            if file_extention == 'xz':
                continue


            # if there are several images with the same shortcode
            if file_extention == 'jpg':
                # img_metadata['jpg_filename'] = []
                img_metadata['jpg_filename'].append(filename)


            # extract data from extention '.json'
            elif file_extention == 'json':

                # read a file
                with open(onefile, encoding='utf-8') as f:
                    data = json.load(f)

                    comments = {}

                    # collect comments
                    for i in range(len(data)):
                        comments_username = data[i]['owner']['username'] 
                        comments_text = data[i]['text']
                        comments[comments_username] = comments_text

                    img_metadata['comments'] = comments



            elif file_extention == 'txt':


                # extract data from extention '_location.txt'
                if filename.split('_')[-1] == 'location.txt':

                    # read a file
                    with open(onefile, 'r', encoding='utf-8') as f:
                        data = f.readlines()
                        gps = data[0].split('\n')[0]
                        gps_detail = data[1]

                        img_metadata['gps'] = gps
                        img_metadata['gps_detail'] = gps_detail


                # extract data from extention just '.txt'
                else:

                    # read a file
                    with open(onefile, 'r', encoding='utf-8') as f:
                        data = f.read()

                        # data format : date_utc:{date_utc}\ncaption:{caption}\nlikes:{likes}\ncomments:{comments}
                        parsed_data = data.split('\\n')

                        date_utc = parsed_data[0].split('date_utc')[1][1:]
                        likes_num = parsed_data[2].split('likes')[1][1:]
                        comments_num = parsed_data[3].split('comments')[1][1:].split('\n')[0]
                        body_text = parsed_data[1].split('caption:')[1]
                        hashtags = [i for i in body_text.split() if i.startswith("#")]
                        hashtags_num = len(hashtags)

                        img_metadata['date_utc'] = date_utc
                        img_metadata['likes_num'] = likes_num
                        img_metadata['comments_num'] = comments_num
                        img_metadata['body_text'] = body_text
                        img_metadata['hashtags'] = hashtags
                        img_metadata['hashtags_num'] = hashtags_num

            print(f'메타데이터 리스트: {img_data_sum}\n\n')

            if idx == (len_images-1):
                # write accumulated metadata into csv file
                # open file
                with open(csv_filename, 'a', newline='', encoding='utf-8') as f: 
                        
                    writer = csv.writer(f)

                    ## make rowlist by using img_metadata
                    rowlist = []

                    imgs_len_in_posting = len(img_data_sum[shortcode]['jpg_filename'])
                    print(f'포스팅의 사진은 몇개 = {imgs_len_in_posting}')

                    for i in range(imgs_len_in_posting):

                        rowlist.append([
                            img_num,
                            img_data_sum[shortcode]['jpg_filename'][i],
                            shortcode,
                            img_data_sum[shortcode]['date_utc'], 
                            int(img_data_sum[shortcode]['likes_num']), 
                            img_data_sum[shortcode]['body_text'],
                            str(img_data_sum[shortcode]['comments']),
                            int(img_data_sum[shortcode]['comments_num']),
                            str(img_data_sum[shortcode]['hashtags']),
                            int(img_data_sum[shortcode]['hashtags_num']),
                            img_data_sum[shortcode]['gps'],
                            img_data_sum[shortcode]['gps_detail']
                        ])

                        img_num += 1

                    print(f'뭘 쓸꺼냐면 : {rowlist}')

                    ## write one row
                    writer.writerows(rowlist)