class ApiHandler {
    constructor({imgBuffer}) {
        this.imgBuffer = imgBuffer
    }

    async send() {
        const url = "/api/exam/review"
        const body = {
            "choicesCount": 5,
            "questionCount": 20,
            "examPhotoType": 0,
            "examPhoto": this.imgBuffer
        }

        document.body.classList.add("loading")
        document.getElementById("send").classList.add("loading")
        document.getElementById("send").disabled = true;

        await fetch(url, {
            method: 'POST',
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(body)
        })
            .then(res => res.json())
            .then(data => {
                if (this.dataHasErr(data)) {
                    this.handleApiError(data)
                } else if (Number(data["iddisciplina"]) === 0) {
                    data["iddisciplina"] = this.askForNumber("A disciplina está zerada", "Adicione seu id dessa disciplina")
                    this.testData = data
                } else {
                    this.testData = data
                    return;
                }
            })
            .catch(err => console.log(err))
            .finally(() => {
                document.body.classList.remove("loading")
                document.getElementById("send").classList.remove("loading")
                document.getElementById("send").disabled = false;
            })
    }

    
    handleApiError(data) {
        const errors = data["err"];

        const errStr = Object.entries(errors).reduce((acc, cur) => acc + `\n${cur[0]}: ${cur[1]}`, '').slice(1);
        try {
            return Swal.fire({
                text: errStr,
                icon: "error"
            });
        } catch(e) {
            window.alert(errStr);
        }
    }

    handleAlert(
        title,
        input,
        {
            inputLabel = "Digite o CPF do aluno em específico",
            inputPlaceholder = "ex.: 654321",
            inputAttributes = {
                maxlength: "10",
                autocapitalize: "off",
                autocorrect: "off"
            }
    } = {}) {
        try {
            return Swal.fire({
                title,
                input,
                inputLabel,
                inputPlaceholder,
                inputAttributes
            })
                .then(data => data.value)
        } catch(e) {
            return window.prompt(inputLabel);
        }
    }

    askForNumber(
        title,
        inputLabel,
        inputPlaceholder = "ex.: 654321",
        inputAttributes = {"maxlength" : "15"}
    ) {
        try {
            return Swal.fire({
                title,
                input: "tel",
                inputLabel,
                inputPlaceholder: inputPlaceholder,
                inputAttributes: {
                    maxlength: inputAttributes["maxlength"],
                    autocapitalize: "off",
                    autocorrect: "off"
                }
            })
                .then(data => data.value)
        } catch(e) {
            if (inputLabel) {
                return window.prompt(`${title}: ${inputLabel}`);
            } else {
                return window.prompt(`${title}`);
            }
        }
    }

    dataHasErr(data) {
        if (!("err" in data)) return false
        if (!(data["err"])) return false
        if (Object.entries(data["err"]).length === 0) return false
        return true
    }

    sendSuccessMessage(title) {
        try {
            return Swal.fire({
                text: title,
                icon: "success"
            });
        } catch(e) {
            alert(title); 
        }
    }
}


class SchoolApiHandler extends ApiHandler {
    constructor({testData, schoolUrl}) {
        super({imgBuffer:testData["marked"]})
        this.testData = testData
        this.url = schoolUrl
    }

    handleIbrepApiAnswer(answer) {
        return Swal.fire({
            html: `<div>Aluno: ${answer["aluno"][0]["aluno"]}</div><div>\nNota: ${answer['nota']}</div>`,
            icon: 'success'
        });
    }

    async send() {
        let cpf
        let protocolo
        const url = this.url

        while (true) {
            cpf = await this.askForNumber("Digite o CPF do aluno", "Digite o CPF do aluno em específico")
            protocolo = await this.askForNumber("Digite o protocolo", "Digite o protocolo de arquivo da prova")

            cpf = Number(cpf)

            if (cpf && protocolo) {
                break
            }
            Swal.fire({
                text: "Necessito do CPF do aluno em questão.",
                icon: "error"
            })
        }

        const iddisciplina = Number(this.testData["iddisciplina"])
        const nota = Number(this.testData["score"])
        const idtipo = Number(this.testData["idtipo"])
        const idmodelo = Number(this.testData["idmodelo"])
        const marked = this.testData["marked"]
        const idprova_impressa = this.testData["idprova_impressa"]

        const body = {
            cpf,
            iddisciplina,
            nota,
            idtipo,
            idmodelo,
            protocolo,
            marked,
            id_solicitacao_prova:this.id_solicitacao_prova,
            idprova_impressa
        }

        document.body.classList.add("loading")

        await fetch(url, {
            method: 'POST',
            body: JSON.stringify(body)
        })
        .then(res => res.json())
        .then(async data => {
            if ('follow_up' in data) {
                this.handleApiError({"err": {"1": "Existem mais de 1 prova para esse aluno hoje. Por favor, contacte o IBREP para mais informações."}})
                return;
                this.handleIbrepApiFollowUp(data);
            } else if (!this.dataHasErr(data)) {
                this.data = data
            } else {
                this.handleApiError(data);
            }
        })
        .finally(() => {
            document.body.classList.remove("loading")
        })
    }
}