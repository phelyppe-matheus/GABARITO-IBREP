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
    constructor({testData, schoolUrl, protocolo}) {
        super({imgBuffer:testData["marked"]})
        this.testData = testData
        this.url = schoolUrl
        this.protocolo = protocolo
    }

    handleIbrepApiAnswer(answer) {
        return Swal.fire({
            html: `<div>Aluno: ${answer["aluno"][0]["aluno"]}</div><div>\nNota: ${answer['nota']}</div>`,
            icon: 'success'
        });
    }

    async send() {
        let cpf;

        while (true) {
            cpf = await this.askForNumber("Digite o CPF do aluno", "Digite o CPF do aluno em específico")

            if (cpf && this.protocolo) {
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
        const protocolo = this.protocolo;

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

        await this.handleFetch(body);
    }

    async handleFetch(body) {
        const url = this.url;
        document.body.classList.add("loading")

        await fetch(url, {
            method: 'POST',
            body: JSON.stringify(body)
        })
            .then(res => res.json())
            .then(async data => {
                if ('follow_up' in data) {
                    document.body.classList.remove("loading")
                    await this.handleIbrepApiFollowUp(data, body);
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

    async handleIbrepApiFollowUp(data, fetchBody) {
        const provas = data.follow_up;
    
        // Gera uma lista de opções para o usuário escolher
        const inputOptions = provas.reduce((options, prova, index) => {
            const label = `
                ${prova.aluno} - ${prova.polo || "Polo não informado"}<br/>
                Prova: ${prova.data_realizacao} das ${prova.de} às ${prova.ate}
            `;
            options[index] = label;
            return options;
        }, {});
    
        const { value: selectedIndex } = await Swal.fire({
            title: 'Selecione a prova correta',
            html: 'Encontramos múltiplas provas para este aluno hoje.<br>Escolha a prova correspondente:',
            input: 'radio',
            inputOptions: inputOptions,
            inputValidator: (value) => {
                if (value === null) {
                    return 'Você precisa selecionar uma das provas.';
                }
            },
            showCancelButton: true,
            cancelButtonText: 'Cancelar',
            confirmButtonText: 'Confirmar',
            allowOutsideClick: false
        });
    
        if (selectedIndex !== undefined) {
            const selectedProva = provas[selectedIndex];
    
            // Chama o fluxo novamente com a idmatricula escolhida
            fetchBody["id_solicitacao_prova"] = selectedProva.id_solicitacao_prova;
            await this.handleFetch(fetchBody);
        } else {
            Swal.fire({
                title: 'Operação cancelada',
                icon: 'info',
                text: 'Nenhuma prova foi selecionada.'
            });
        }
    }    
}