
$("#imageFile").change(function (event) {

    var oFReader = new FileReader();
    oFReader.readAsDataURL(document.getElementById("imageFile").files[0]);

    oFReader.onload = function (oFREvent) {
        document.getElementById("clientImage").src = oFREvent.target.result;
    };
    $("#clientImage").fadeIn(250);
});