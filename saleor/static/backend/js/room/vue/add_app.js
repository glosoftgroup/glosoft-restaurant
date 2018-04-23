$ = jQuery;
//var dataForm = $('#room-form');
var amenities = $('.amenities');
var uploadImageUrl = $('.pageUrls').data('uploadimages');
var csrfmiddlewaretoken  = jQuery("[name=csrfmiddlewaretoken]").val();

function alertUser(msg,status='bg-success',header='Well done!')
{ $.jGrowl(msg,{header: header,theme: status}); }

Vue.component('select2',{
    props: ['options', 'value'],
    template: '#select2-template',
    mounted: function(){
        var vm = this;
        $(this.$el)
        // init select2
        .select2({ data: this.options })
        .val(this.value)
        .trigger('change')
        // emit event on chage
        .on('change', function(){
            vm.$emit('input', this.value)
        })
    },
    watch: {
        value: function(value){
            //update value
            $(this.$el)
            .val(value)
            .trigger('change')
        },
        options: function(options){
            // update options
            if(this.value){
                $(this.$el).empty().select2({ data: options}).val(this.value).trigger('change')
            }else{
                $(this.$el).empty().select2({ data: options})
            }
        }
    },
    destroyed: function(){
        $(this.$el).off().select2('destroy')
    }
});

var parent = new Vue({
    el:"#vue-app",
    delimiters: ['${', '}'],
    data:{
       name: '',
       bedrooms: '',
       amenities: [],
       units: 0,
       floor_space: 0,
       price: 0,
       description: '',
       service_charges: 0,
       autoComplete: true,
       nightly: null,
       daytime: null,
       weekly : null,
       daily  : null,
       monthly: null,
       wing: 1,
       wing_options: [],
       errors: {},
       propertytype: 3,
       propertytype_options: []
    },
    components: {
        UploadImage
    },
    mounted:function(){

       var self = this;
       axios.defaults.xsrfHeaderName = "X-CSRFToken";
       axios.defaults.xsrfCookieName = 'csrftoken';

       // fetch wing options
       axios.get('/wing/api/list/')
       .then(function (response) {
           self.wing_options = response.data.results
       })
       .catch(function (error) {
            console.log(error);
       });

       // fetch property types
       axios.get('/propertytype/api/list/')
       .then(function (response) {
           self.propertytype_options = response.data.results
       })
       .catch(function (error) {
            console.log(error);
       });

       if($('#wing_id').val()){
           this.wing = $('#wing_id').val();
       }
       if($('#type_id').val()){
           this.propertytype = $('#type_id').val();
       }

       //console.log(today);
    },
    methods:{
        handleChange(event){
            const target = event.target;
            const name = target.name;

            if(!!this.errors[name]){
                delete this.errors[name];
            }
        },
        addInstance(e){
            e.preventDefault()
            // validation
            let errors = {};
            if(this.name === '') errors.name = 'This field is required';
            if(this.bedrooms === 0) errors.bedrooms = 'This field is required';
            if(!this.wing) errors.wing = 'This field is required';
            if(!this.propertytype) errors.propertytype = 'This field is required';
            if(!this.units) errors.units = 'This field is required';
            if(!this.price) errors.price = 'This field is required';
            if(!this.service_charges) errors.service_charges = 'This field is required';
            if(!this.floor_space) errors.floor_space = 'This field is required';
            this.errors = errors;
            console.error(amenities);
            console.error(amenities.val());
            if(!amenities.val())
            {
                amenities.nextAll('.help-block:first').addClass('text-warning').html('This field is required');
                return false;
            }

            // prepare data
            var data = new FormData()

            data.append('name', this.name)
            data.append('bedrooms', this.bedrooms)
            data.append('units', this.units)
            data.append('price', this.price)
            data.append('service_charges', this.service_charges)
            data.append('floor_space', this.floor_space)
            data.append('wing', this.wing)
            data.append('propertytype', this.propertytype)
            data.append('amenities', JSON.stringify(amenities.val()))
            console.log('sending details')

        }
    },
    watch:{
        wing: function(value,old){

        }
    }
});

var showImages = Vue.component('show-images',{
    template: '#show-images',
    delimiters: ['${', '}'],
    props:{
        rooms:{
            type: Array,
            required: false,
            default: []
        },
        refresh: {required: false}
    },
    methods: {
        deleteImage(id){
            var url = '/dashboard/room/delete/image/'+id;
            axios.defaults.xsrfHeaderName = "X-CSRFToken"
            axios.defaults.xsrfCookieName = 'csrftoken'

            axios.delete(url)
            .then((data)=>{
                console.log($('#delete-image'+id));
                $('#delete-image'+id).addClass('hidden').remove();
                // this.$emit('refresh');
                this.refresh();
            })
            .catch((error)=>{
                console.log(error);
            })
        }
    }
});

var UploadImage = Vue.component('upload-image', {
        template: '#uploader-temp',
        delimiters: ['${', '}'],
        props: {
            url: {
                type: String,
                required: true,
                default: null
            },
            name: {
                type: String,
                required: false,
                default: 'images[]'
            },
            max_batch: {
                type: Number,
                required: false,
                default: 0
            },
            max_files: {
                type: Number,
                required: false,
                default: 10
            },
            max_filesize: {
                type: Number,
                required: false,
                default: 8000
            },
            button_html: {
                type: String,
                required: false,
                default: 'Upload Images'
            },
            button_class: {
                type: String,
                required: false,
                default: 'btn btn-primary'
            },
        },
        data: function(){
            return {
                form: null,
                input: null,
                index: 0,
                total: 0,
                files: {},
                image: {},
                batch: {},
                room_images:[],
                onDragover: false,
                onUploading: false
            }
        },
        mounted: function(){
            this._refresh_images();
            this.form = document.getElementById('upload_image_form--' + this.name);
            this.input = document.getElementById('upload_image_form__input--' + this.name);

            ['drag', 'dragstart', 'dragend',
                'dragover', 'dragenter', 'dragleave', 'drop'].forEach(event => this.form.addEventListener(event, (e) => {
                e.preventDefault(); e.stopPropagation();
            }));

            ['dragover', 'dragenter']
                .forEach(event => this.form.addEventListener(event, this.dragEnter));

            ['dragleave', 'dragend', 'drop']
                .forEach(event => this.form.addEventListener(event, this.dragLeave));

            ['drop']
                .forEach(event => this.form.addEventListener(event, this.fileDrop));

            ['change']
                .forEach(event => this.input.addEventListener(event, this.fileDrop));

            this.form.addEventListener('click', (e) => {
                this.input.click();
            });
        },
        methods: {
            _can_xhr(){
                if(this.total >= this.max_files){
                    return false;
                }
                return true;
            },
            _can_upload_file(key){
                let file = this.files[key];

                if(file.attempted || file.bad_size){
                    return false;
                }
                return true;
            },
            _processImages(data){
                if(data){
                    if(full) return data.image.medium_square_crop;
                        return data.image.medium_square_crop;
                }
                return '/static/backend/images/rooms/room.jpg';
            },
            _refresh_images(){
                console.log('refreshing...')
                this.$http.get('/api/property/image/?q='+pk)
                .then(function(data){
                    data = JSON.parse(data.bodyText);
                    this.room_images = data.results;
                }, function(error){
                    console.log(error.statusText);
                });
            },
            _xhr: function(formData, keys, callback){
                this.onUploading = true;
                this.$emit('upload-image-attempt', formData);

                keys.forEach((key) => {
                    Vue.set(this.files[key], 'attempted', true);
                });

                this.$http.post(this.url, formData).then((response) => {
                    keys.forEach((key) => {
                        Vue.set(this.files[key], 'uploaded', true);
                        this.total++;
                    });

                    alertUser('Image added successfully');
                    this._refresh_images();
                    this.$emit('upload-image-success', [formData, response]);
                }, (response) => {
                    this.$emit('upload-image-failure', [formData, response]);
                }).then((response) => {
                    this.onUploading = false;

                    callback();
                });
            },
            upload: function(){
                if(!this._can_xhr()) return false;

                for (let key in this.files) {
                    if(!this._can_upload_file(key)) continue;

                    let formData = new FormData();
                    formData.append(this.name, this.files[key]);
                    formData.append('csrfmiddlewaretoken', csrfmiddlewaretoken);

                    this._xhr(formData, [key], this.upload);

                    return true;
                }
            },
            upload_batch: function(){
                if(!this._can_xhr()) return false;

                for (let key in this.batch) {
                    this._xhr(this.batch[key].form, this.batch[key].keys, this.upload_batch);

                    delete this.batch[key];

                    return true;
                }
            },
            create_batch: function(){
                let index = 0;
                let count = 0;

                this.batch = {};

                for (let key in this.files) {
                    if(!this._can_upload_file(key)) continue;

                    if(this.batch[index] == null || count == this.max_batch){
                        index++;
                        count = 0;
                        this.batch[index] = {form:new FormData(), keys:[]};
                    }

                    count++;
                    this.batch[index]['keys'].push(key);
                    this.batch[index]['form'].append(this.name, this.files[key]);
                }
            },
            submit: function(e){
                e.preventDefault(); e.stopPropagation();

                if(!this.onUploading){
                    if(this.max_batch > 1){
                               this.create_batch();
                        return this.upload_batch();
                    }
                    this.upload();
                }
            },
            dragEnter: function(e){
                e.preventDefault();
                this.onDragover = true;
            },
            dragLeave: function(e){
                e.preventDefault();
                this.onDragover = false;
            },
            fileDrop: function(e){
                e.preventDefault();

                let newFiles = e.target.files || e.dataTransfer.files;

                for(let i = 0; i < newFiles.length; i++){
                    Vue.set(this.files, this.index, newFiles[i]);
                    this.fileInit(this.index);
                    this.fileRead(this.index);

                    this.index++;
                }

                e.target.value = '';
            },
            fileInit: function(key){
                let file = this.files[key];

                if((file.size * 0.001) > this.max_filesize){
                    Vue.set(this.files[key], 'bad_size', true);
                }
            },
            fileRead: function(key){
                let reader = new FileReader();

                reader.addEventListener("load", (e) => {
                    Vue.set(this.image, key, reader.result);
                });

                reader.readAsDataURL(this.files[key]);
            },
            fileDelete: function(e, key){
                Vue.delete(this.files, key);
                Vue.delete(this.image, key);
            },
            fileView: function(e, key){
                e.preventDefault(); e.stopPropagation();
            }
        }
    });


new Vue({
    el:"#vue-app2",
    delimiters: ['${', '}'],
    data:{
        name:'Upload files'
    },
    template: '<upload-image url="'+uploadImageUrl+'"></upload-image>',
    components: {
        UploadImage
    }
})