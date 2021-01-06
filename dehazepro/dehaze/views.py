from django.shortcuts import render

def index(request):
    return render(request, "index.html")

# Create your views here.

from django.shortcuts import render, redirect
import json
from PIL import Image
from dehaze.model.Unet import Unet
import torch
from torchvision import transforms as T
from django.conf import settings
import os
import base64
from django.http import JsonResponse
print("basedir", settings.BASE_DIR)

model = Unet()
model.load_state_dict(torch.load('dehaze/model/multi_U_151.pth', map_location=torch.device('cpu')))
model.cpu()
model.eval()

def dehaze(input):
    with torch.no_grad():
        result = model(input)

    return result

def upload(request):  
    
    #画像データの取得
    files = request.FILES.getlist('yourFile')
    print(request.FILES)
    print("files", files)
    
    #簡易エラーチェック（jpg拡張子）
    for memory_file in files:
        print("filename", memory_file)
        root, ext = os.path.splitext(memory_file.name)
        print(ext)

    if request.method =='POST' and files:
        result=[]
        labels=[]
        #json_dict = json.loads(request.body)
        #for file in request.body:
            #print("file", file)
        for file in files:
            img = Image.open(file)
            y,x = img.size
            img1 = T.Resize(((x//8)*8,(y//8)*8))(img)
            img_te = T.ToTensor()(img1)
            img_te = img_te.unsqueeze(0)
            img_r = dehaze(img_te)
            img_r = img_r.squeeze(0).mul(255).add_(0.5).clamp_(0, 255).permute(1, 2, 0).to('cpu', torch.uint8).numpy()
            img_r = Image.fromarray(img_r)
            input_path = os.path.join(settings.BASE_DIR,'dehaze','static', 'img','input.jpg')
            output_path = os.path.join(settings.BASE_DIR,'dehaze','static','img','output.jpg')
            img.save(input_path)
            img_r.save(output_path)

            with open(input_path, 'rb') as f:
                in_data = f.read()
            data1=base64.b64encode(in_data)
            data1 = str(data1)[2:-1]
                        
            with open(output_path, 'rb') as f:
                out_data = f.read()
            data2=base64.b64encode(out_data)
            data2 = str(data2)[2:-1]

            result.append((data1, data2))

        context = {
            'result': result
            }
        #context = context.values()
        #col = list(context)
        
        return JsonResponse(data=context)
            
        #return render(request, 'result.html', context)
    else:
        context = {
            'result': ""
            }
        context = context.values()
        col = list(context)
        return JsonResponse(data=col, safe=False)