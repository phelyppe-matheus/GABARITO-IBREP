class GabaritoCam {
    constructor({webCamElement, canvasToSend}) {
        this.webCamElement = webCamElement
        this.canvasToSend = canvasToSend

        navigator.mediaDevices
            .getUserMedia({ video: { facingMode: "environment", resizeMode: "none" }, audio: false })
            .then((stream) => {
                this.webCamElement.srcObject = stream
                this.webCamElement.play()
                this.webCamStream = stream
                this.track = this.webCamStream.getVideoTracks()[0];
            })
            .catch((err) => {
                console.error(`An error occurred: ${err}`)
            });
    }

    torch() {
        this.track.applyConstraints({ advanced: [{ torch: true }] })
        return true
    }

    askForFullScreen() {
        return Swal.fire({
            title: "Permite tela cheia?",
            text: "Com a tela cheia, você pode usar o aplicativo mais eficientemente",
            showCancelButton: true,
            confirmButtonText: "Permitir",
            confirmButtonAriaLabel: "Permitir o uso do aplicativo em tela cheia",
            cancelButtonText: "Melhor não, obrigado",
            cancelButtonAriaLabel: "Não permitir o uso do aplicatico em tela cheia"
        }).then((result) => {
            if (result.isConfirmed) {
                document.body.requestFullscreen();
            } 
        })
    }

    
    snap() {
        this.webCamElement.play()
        const track = this.webCamStream.getVideoTracks()[0];
        const streamSettings = track.getSettings();
        let imgCapture = new ImageCapture(track);

        document.getElementById("snap").classList.add("loading");
        imgCapture.takePhoto()
            .then(blob => {
                let img = new Image();
                this.webCamElement.pause();

                img.onload = () => {
                    this.canvasToSend.height = img.naturalHeight;
                    this.canvasToSend.width = img.naturalWidth;
                    this.canvasToSend.getContext("2d").drawImage(img, 0, 0);
                    this.imgBuffer = this.canvasToSend.toDataURL();
                    this.showImg(this.imgBuffer, "")
                    document.getElementById("snap").classList.remove("loading");
                }

                img.src = URL.createObjectURL(blob);
            })
    }

    retry() {
        this.webCamElement.play();
    }

    showImg(img, title) {
        return Swal.fire({
            title: title,
            imageUrl: img,
        });
    }
}