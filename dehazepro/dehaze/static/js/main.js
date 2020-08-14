function sendRequest(url, method, data){
  var r = axios({
      method: method,
      url: url,
      data: data,
      xsrfCookieName: 'csrftoken',
      xsrfHeaderName: 'x-CSRFToken',
      headers: {
          'X-Requested-with': 'XMLHttpRequest'
      }
  })
  return r
  }

var vm = new Vue({

    el: '#app',
    delimiters: ['[[', ']]'],
    
    data: function () {
                  return{        
          msg: "{% static 'img/sample1.jpg' %}",
          result:[],
          file:"",
          files:[],
          uploadedImage: '',
          img_name: '',
          output:"",
          dataUrl: "",
          name:"",
          sample1:"static/img/sample1.jpg",
          sample2:"static/img/sample2.jpg",
          sample3:"static/img/sample3.jpg",
          
                  }
              },
    methods: {
        showMessage:function () {
            this.msg = "{% static 'img/sample1.jpg' %}";
            console.log(this.msg);
        },
        deleteMessage:function () {
            this.msg = "";
        },

        sendimage:function(){
          var formData = new FormData();
          formData.append('yourFile',this.file);
          console.log(this.file);
          console.log(formData);
          sendRequest('processing/','post',formData)
          .then(function(response){
            var name = response
            console.log(name)
          })
  
        },   

        sendmessage:function(){
          console.log(this.file);
          var formData = new FormData();
          formData.append('yourFile',this.file);
          

          sendRequest('upload/','post',formData)
          .then(function(response){
            for(var d in response.data){
              var item = response.data[d]
              vm.result.push(item)
              vm.output=(item[0][1])
              const prefix = 'data:image/jpg;base64,';
              vm.dataUrl = prefix + vm.output;            
            }
  
          })
        },
        onFileChange(e) {
        this.output = "";
        const files = e.target.files || e.dataTransfer.files;
        this.createImage(files[0]);
        this.file = files[0]
        this.img_name = files[0].name;
        this.item = {
          "name":this.img_name
        };
        },
      // アップロードした画像を表示
        createImage(file) {
          const reader = new FileReader();
          reader.onload = e => {
            this.uploadedImage = e.target.result;
          };
          reader.readAsDataURL(file);
        },
        remove() {
          this.uploadedImage = false;
          this.img_name = false;
          this.output = false;
        },
          
        test1(e){
          console.log(e.target.value)
          
          try{
          this.uploadedImage = false;
          var xhr = new XMLHttpRequest();
          if(e.target.value=="1"){
          　xhr.open('GET', this.sample1, true);
          }
          else if(e.target.value=="2"){
            xhr.open('GET', this.sample2, true);
          }
          else if(e.target.value=="3"){
          　xhr.open('GET', this.sample3, true);
          }
          xhr.responseType = 'arraybuffer';
          xhr.onload = function(e) {
            var arrayBuffer = this.response;
        
            // Fileを生成する
            var blob = new File([arrayBuffer], vm.sample1 ,{type: "image/jpg"});
            vm.file = blob;
            console.log(vm.file)
            
          };
          xhr.send();
        }catch(e){
          console.log("select a image");
        }
        
          
        },
        
      }
    });