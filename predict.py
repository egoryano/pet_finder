import cv2
import os
import numpy as np
import pandas as pd
from sklearn.neighbors import NearestNeighbors
from keras.applications.densenet import preprocess_input, DenseNet121
from keras.models import Model
from keras.layers import GlobalAveragePooling2D, Input, Lambda, AveragePooling1D
import keras.backend as K
from tensorflow import keras


img_size = 256


def resize_to_square(im):
    old_size = im.shape[:2] # old_size is in (height, width) format
    ratio = float(img_size)/max(old_size)
    new_size = tuple([int(x*ratio) for x in old_size])
    # new_size should be in (width, height) format
    im = cv2.resize(im, (new_size[1], new_size[0]))
    delta_w = img_size - new_size[1]
    delta_h = img_size - new_size[0]
    top, bottom = delta_h//2, delta_h-(delta_h//2)
    left, right = delta_w//2, delta_w-(delta_w//2)
    color = [0, 0, 0]
    new_im = cv2.copyMakeBorder(im, top, bottom, left, right, cv2.BORDER_CONSTANT,value=color)

    return new_im

def load_image(path, pet_id):
    image = cv2.imread(f'{path}{pet_id}-1.jpg')
    new_image = resize_to_square(image)
    new_image = preprocess_input(new_image)

    return new_image


def load_emb_model(weights_path):
    inp = Input((256,256,3))
    backbone = DenseNet121(input_tensor = inp, include_top = False, weights=None)
    backbone.load_weights(weights_path)
    x = backbone.output
    x = GlobalAveragePooling2D()(x)
    x = Lambda(lambda x: K.expand_dims(x,axis = -1))(x)
    x = AveragePooling1D(4)(x)
    out = Lambda(lambda x: x[:,:,0])(x)

    return Model(inp,out)


def load_image(path):
    image = cv2.imread(f'{path}')
    new_image = resize_to_square(image)
    new_image = preprocess_input(new_image)

    return new_image


def get_embeddings(emb_model, photos_names, path):
    print(photos_names)
    photos = [load_image(f'{path}/{img_name}') for img_name in photos_names]
    photos = np.array(photos)
    embs = emb_model.predict(photos)
    
    return embs


def get_nearest_ids(train_embs, search_img_emb):
    neigh = NearestNeighbors(n_neighbors=2, radius=0.4)
    neigh.fit(train_embs)
    closest_pets = neigh.kneighbors(search_img_emb, 5, return_distance=False)
    
    return closest_pets


def get_closest_img_names(filtered_img_names,
                      img_path,
                      search_img_name,
                      search_path,
                      weights_path):
    
    emb_model = load_emb_model(weights_path)
    print(filtered_img_names)
    train_embs = get_embeddings(emb_model, filtered_img_names, img_path)
    search_img_emb = get_embeddings(emb_model, [search_img_name], search_path)
    closest_ids = get_nearest_ids(train_embs, search_img_emb)
    closest_pets_img_names = np.array(filtered_img_names)[closest_ids][0]
    # remove extension
    closest_pets_card_names = set([name.split('.')[0] for name in closest_pets_img_names])
    
    return closest_pets_card_names
