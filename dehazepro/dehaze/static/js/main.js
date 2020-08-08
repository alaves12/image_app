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
                  }
              },
    methods: {
        showMessage: function () {
            this.msg = "{% static 'img/sample1.jpg' %}";
            console.log(this.msg);
        },
        deleteMessage: function () {
            this.msg = "";
        },
        sendmessage: function(){
          csrftoken = Cookies.get('csrftoken');
          headers = {'X-CSRFToken': csrftoken};
          let formData = new FormData();
          formData.append('yourFile', this.file);
          axios.post('upload/', formData, {headers: headers})
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
        },
    
        
        }
    });