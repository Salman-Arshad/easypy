var editor = ace.edit("editor");

var unsaved = true;

// editor.setTheme("ace/theme/chrome");
editor.setTheme("ace/theme/dawn");
editor.session.setMode("ace/mode/python");

editor.commands.addCommand({
    name: "execute",
    exec: function() {submitRun();},
    bindKey: {win: "ctrl-enter"}
});


editor.on('change', function(delta) {
    null;
});


function wrapUnsaved(content){
    unsaved = false;
    editor.setValue(content);
    unsaved = true;
}

function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}


// Begin File Manager Functions
function getSelectedFile(){
    var selectedH3 = document.getElementById('file-name');
    return document.getElementById(selectedH3.innerHTML.replace('(unsaved)',''));
}

var elements = document.getElementsByClassName("file-dir");
for (var i = 0; i < elements.length; i++) {
    elements[i].addEventListener('click', selectFile, false);
}

function toggleTree(elem, target){
    var display = (elem.innerHTML=='+') ? 'block' : 'none';
    elem.innerHTML = (display == 'none') ? '+' : '-';
    Array.prototype.slice.call(document.getElementById(target).getElementsByTagName('li')).forEach(function(li){
       li.style.display = display;
    });
}

function toggleSelected(element){
    element.classList.toggle("badge");
    element.classList.toggle("badge-primary");
}

function selectFile(event){
    var selectedH3 = document.getElementById('file-name');
    if (selectedH3.innerHTML.endsWith('(unsaved)')){
        selectedH3.innerHTML = selectedH3.innerHTML.replace('(unsaved)','');
        unsaved = true;
    }

    var currentSelected = document.getElementById(selectedH3.innerHTML);
    //when first load there is none selected element
    if (currentSelected){
        toggleSelected(currentSelected);
    }

    toggleSelected(event.target);
    selectedH3.innerHTML = event.target.id;
    getContent();
    //control buttons
    document.getElementById('ctrl-btn-delete').disabled = false;
    document.getElementById('ctrl-btn-rename').disabled = false;
    document.getElementById('parent-abspath').value = event.target.id;
    if(event.target.getAttribute("directory")){
        document.getElementById('upload-location').value = event.target.id;
        document.getElementById('ctrl-btn-upload').disabled = false;
        document.getElementById('ctrl-btn-new-dir').disabled = false;
        document.getElementById('ctrl-btn-new-file').disabled = false;
        document.getElementById('ctrl-btn-save').disabled = true;
    }else{
        document.getElementById('ctrl-btn-upload').disabled = true;
        document.getElementById('ctrl-btn-new-dir').disabled = true;
        document.getElementById('ctrl-btn-new-file').disabled = true;
        document.getElementById('ctrl-btn-save').disabled = false;
    }
}
// End File Manager Functions

//SIDEBAR
$(document).ready(function () {
    $('#sidebarCollapse').on('click', function () {
        $('#sidebar').toggleClass('active');
    });
    $(function () {
        $('[data-toggle="tooltip"]').tooltip()
    });
});



//CONTROL BUTTONS
$('#createFileModal').on('shown.bs.modal', function () {
    $('#new-file-name').focus();
});
function setNewFileType(type){
    document.getElementById('new-file-type').value = type;
    var submitName = (type == 'rename') ? 'Rename' : 'Create';
    document.getElementById('new-file-submit').innerHTML = submitName;
}

function wipe(){
    wrapUnsaved('');
    var selectedH3 = document.getElementById('file-name');
    var currentSelected = document.getElementById(selectedH3.innerHTML);
    if (currentSelected){
        toggleSelected(currentSelected);
    }
    selectedH3.innerHTML = '';
    document.getElementById('stdout').innerHTML = '';
    //disable all ctrl buttons
    document.getElementById('ctrl-btn-delete').disabled = true;
    document.getElementById('ctrl-btn-upload').disabled = true;
    document.getElementById('ctrl-btn-new-dir').disabled = true;
    document.getElementById('ctrl-btn-new-file').disabled = true;
    document.getElementById('ctrl-btn-save').disabled = true;
}

function submitRun(){
    document.getElementById('dialogoverlay').style.display = 'block';
    var data = {};
    data['operation'] = 'run';
    data['content'] = editor.getValue();
    $.ajax({
        type: "POST",
        beforeSend: function(request) {
            request.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
        },
        url: "/",
        data: data, //JSON.stringify(data),
        //contentType: "application/json; charset=utf-8",
        dataType: "json",
        success: function(response){
            console.log('run ok');
            document.getElementById('stdout').innerHTML = response['stdout'];
        },
        error: function(errMsg) {
            console.log('error when run');
            console.log(errMsg);
            console.log(errMsg.responseText);
        },
    }).always(function(){
        document.getElementById('dialogoverlay').style.display = 'none';
    });
}


function submitSave(){
    if (!(getSelectedFile().getAttribute('directory'))){
        var data = {};
        var fileName = document.getElementById('file-name');
        fileName.innerHTML = fileName.innerHTML.replace('(unsaved)','');
        data['operation'] = 'save';
        data['content'] = editor.getValue();
        data['file'] = fileName.innerHTML;
        $.ajax({
            type: "POST",
            beforeSend: function(request) {
                request.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
            },
            url: "/",
            data: data, //JSON.stringify(data),
            //contentType: "application/json; charset=utf-8",
            dataType: "json",
            success: function(response){
                document.getElementById('stdout').innerHTML = 'saved';
                unsaved = true;
            },
            error: function(errMsg) {
                console.log('error when saving');
                console.log(errMsg);
                console.log(errMsg.responseText);
            },
        });
    }
}

function getContent(){
    if (getSelectedFile().getAttribute('directory')){
        wrapUnsaved('');
        editor.setReadOnly(true);
        document.getElementById('stdout').innerHTML = getSelectedFile().id + " it's a directory";
    }else{
        $.ajax({
            type: "POST",
            beforeSend: function(request) {
                request.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
            },
            url: "/content/",
            data: {'file': document.getElementById('file-name').innerHTML}, //JSON.stringify(data),
            //contentType: "application/json; charset=utf-8",
            dataType: "json",
            success: function(response){
                wrapUnsaved(response['content']);
                document.getElementById('stdout').innerHTML = '';
                editor.setReadOnly(false);
            },
            error: function(errMsg) {
                wrapUnsaved('');
                document.getElementById('stdout').innerHTML = JSON.parse(errMsg.responseText)['description'];
                document.getElementById('ctrl-btn-save').disabled = true;
                editor.setReadOnly(true);
            }
        });
    }
}

function rmFile(){
    var file = document.getElementById('file-name').innerHTML;
    $.ajax({
        type: "POST",
        beforeSend: function(request) {
            request.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
        },
        url: "/rm/",
        data: {'file': file}, //JSON.stringify(data),
        //contentType: "application/json; charset=utf-8",
        dataType: "json",
        success: function(response){
            var li = document.getElementById(file).parentNode.parentNode;
            li.parentNode.removeChild(li);
            wipe();
        },
        error: function(errMsg) {
            wrapUnsaved('');
            document.getElementById('stdout').innerHTML = JSON.parse(errMsg.responseText)['description'];
        }
    });
}

function createFile(){
    $("#createFileModal").modal("hide");
    var type = document.getElementById('new-file-type').value;
    var parent = document.getElementById('parent-abspath').value;
    var name = document.getElementById('new-file-name').value;

    $.ajax({
        type: "POST",
        beforeSend: function(request) {
            request.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
        },
        url: "/create/",
        data: {'type': type, 'parent': parent, 'name': name}, //JSON.stringify(data),
        //contentType: "application/json; charset=utf-8",
        dataType: "json",
        success: function(response){
            console.log(response);
            if (type != 'rename'){
                document.getElementById('ul'+parent).innerHTML += response['content'];
                var elements = document.getElementsByClassName("file-dir");
                for (var i = 0; i < elements.length; i++) {
                    elements[i].addEventListener('click', selectFile, false);
                }
            }else{

                var spanElem = document.getElementById(parent);
                spanElem.id = response['content']['abs_path'];
                spanElem.innerHTML = response['content']['name'];
                document.getElementById('file-name').innerHTML = response['content']['abs_path'];
                document.getElementById('parent-abspath').value = response['content']['abs_path'];
                if(spanElem.getAttribute("directory")){
                    var ul = document.getElementById('ul'+parent);
                    ul.id = 'ul' + response['content']['abs_path'];
                }
                window.location.reload();
            }
        },
        error: function(errMsg) {
            wrapUnsaved('');
            document.getElementById('stdout').innerHTML = JSON.parse(errMsg.responseText)['description'];
        }
    }).always(function(){
        document.getElementById('new-file-name').value = '';
    });
}
