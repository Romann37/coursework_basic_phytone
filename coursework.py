import json
import requests
import time
from tqdm import tqdm


class Photo:

    def __init__(self, vkid, yadisk_token):
        self.vk_token = input("введите токен для ВК: ")
        self.yadisk_token = input("введите токен для Ядиск: ")
        self.id = vkid

    def get_headers(self):
        return {"Content-Type": "application/json",
                "Authorization": f"OAuth {self.yadisk_token}"}

    def get_number_id(self):
        number = requests.get("https://api.vk.com/method/users.get", params={"access_token": self.vk_token,
                                                                             "v": "5.131", "user_ids": f"{self.id}"})
        return number.json()['response'][0]['id']

    def get_photo_vk(self):
        photos_dict = {}
        result = requests.get("https://api.vk.com/method/photos.get", params={"access_token": self.vk_token,
                                                                            "owner_id": "417506552",
                                                                            "v": "5.131", "album_id": "profile",
                                                                            "extended": "1"})
        for item in result.json()["response"]["items"]:
            if str(item['likes']['count']) in photos_dict:
                name = str(item['likes']['count']) + '_' + str(item['date'])
                photos_dict[name] = [item["sizes"][-1]['url']]
                photos_dict[name].append(item['sizes'][-1]['type'])
            else:
                name = str(item['likes']['count'])
                photos_dict[name] = [item["sizes"][-1]['url']]
                photos_dict[name].append(item['sizes'][-1]['type'])
        return photos_dict

    def get_url(self):
        url = requests.get('https://cloud-api.yandex.net:443/v1/disk/resources/upload',
                           headers=self.get_headers(),
                           params={"path": f"/photo_VK/", "overwrite": "True"}).json()['href']
        return url

    def upload_yadisk(self):
        # Выполняем проверку наличия папки с нужным имененем на ЯДиске. Если нет то создаем ее.
        if requests.get('https://cloud-api.yandex.net:443/v1/disk/resources', headers=self.get_headers(),
                        params={'path': '/photo_VK'}).status_code == 404:
            requests.put('https://cloud-api.yandex.net:443/v1/disk/resources', headers=self.get_headers(),
                         params={'path': '/photo_VK'})

        # Загружаем фото и создаем список для json-файла
        jsonlist = []
        files = self.get_photo_vk()
        for filename, fileinside in tqdm(files.items()):
            information = {}
            requests.post('https://cloud-api.yandex.net:443/v1/disk/resources/upload', headers=self.get_headers(),
                          params={'path': f"/photo VK/{filename}.jpg", 'url': f"{fileinside[0]}"}).json()
            information["filename"] = f'{filename}.jpg'
            information['size'] = fileinside[1]
            jsonlist.append(information)
            time.sleep(0.5)

        with open('photo.json', 'w', encoding='utf-8') as f:
            json.dump(jsonlist, f, indent=2)

#if __name__ == '__main__':
    # Получаем токен от пользователя и вводим его id VK
yadisk_token = input("введите токен для Ядиск: ")
id_yadisk = input("введите id для ВК: ")
uploader = Photo(id_yadisk, yadisk_token)
result = uploader.upload_yadisk()
   
