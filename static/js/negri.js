// output functions are configurable.  This one just appends some text
// to a pre element.
function outf(text) {
    var mypre = document.getElementById("output");
    mypre.innerHTML = mypre.innerHTML + text;
}
function builtinRead(x) {
    if (Sk.builtinFiles === undefined || Sk.builtinFiles["files"][x] === undefined)
            throw "File not found: '" + x + "'";
    return Sk.builtinFiles["files"][x];
}

function runit() {
   var prog = document.getElementById("yourcode").value;
   var mypre = document.getElementById("output");
   mypre.innerHTML = '';
   Sk.pre = "output";
   Sk.configure({output:outf, read:builtinRead});
   (Sk.TurtleGraphics || (Sk.TurtleGraphics = {})).target = 'mycanvas';
   var myPromise = Sk.misceval.asyncToPromise(function() {
       return Sk.importMainWithBody("<stdin>", false, prog, true);
   });
   myPromise.then(function(mod) {
       console.log('success');
   },
       function(err) {
       console.log(err.toString());
   });
}

$(function() {
  $('textarea[data-editor]').each(function() {
    var textarea = $(this);

    var editDiv = $('<div>', {
      position: 'absolute',
      width: textarea.width(),
      height: textarea.height(),
      'class': textarea.attr('class')
    }).insertBefore(textarea);

    textarea.css('display', 'none');
    var editor = ace.edit(editDiv[0]);
    editor.renderer.setShowGutter(textarea.data('gutter'));
    editor.getSession().setValue(textarea.val());
    editor.setTheme("ace/theme/tomorrow_night");
    editor.getSession().setMode("ace/mode/python");
    editor.setShowPrintMargin(false);
    editor.setOptions({maxLines: 10, fontSize:'20px',});
    //editor.$blockScrolling = Infinity;
    editor.setOptions({
autoScrollEditorIntoView: true,
copyWithEmptySelection: true,
});

    // copy back to textarea on form submit...
    editor.getSession().on('change', function(){
      textarea.val(editor.getSession().getValue());
    })
  });
});


function saveTextAsFile() {
  var textToWrite = document.getElementById('yourcode').innerHTML;
  var textFileAsBlob = new Blob([ textToWrite ], { type: 'text/plain' });
  var fileNameToSaveAs = "test.py"; //filename.extension

  var downloadLink = document.createElement("a");
  downloadLink.download = fileNameToSaveAs;
  downloadLink.innerHTML = "Download File";
  if (window.webkitURL != null) {
    // Chrome allows the link to be clicked without actually adding it to the DOM.
    downloadLink.href = window.webkitURL.createObjectURL(textFileAsBlob);
  } else {
    // Firefox requires the link to be added to the DOM before it can be clicked.
    downloadLink.href = window.URL.createObjectURL(textFileAsBlob);
    downloadLink.onclick = destroyClickedElement;
    downloadLink.style.display = "none";
    document.body.appendChild(downloadLink);
  }

  downloadLink.click();
}

var button = document.getElementById('save');
button.addEventListener('click', saveTextAsFile);

function destroyClickedElement(event) {
  // remove the link from the DOM
  document.body.removeChild(event.target);
}