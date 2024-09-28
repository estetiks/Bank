document.addEventListener("DOMContentLoaded", function() {
    let firstCurrency = null;
    let secondCurrency = null;

    // Функция для обработки нажатия кнопки валюты
    function handleCurrencyButtonClick(button, group, isFirstCurrency) {
        const buttons = group.querySelectorAll(".currency-btn");
        buttons.forEach(btn => btn.classList.remove("active"));
        button.classList.add("active");

        if (isFirstCurrency) {
            firstCurrency = button.dataset.currency;
        } else {
            secondCurrency = button.dataset.currency;
        }

        
    }

    const firstCurrencyButtons = document.querySelectorAll('.currency-input:first-of-type .currency-btn');
    firstCurrencyButtons.forEach(button => {
        button.addEventListener('click', function() {
            handleCurrencyButtonClick(this, this.parentElement, true);
        });
    });

    const secondCurrencyButtons = document.querySelectorAll('.currency-input:last-of-type .currency-btn');
    secondCurrencyButtons.forEach(button => {
        button.addEventListener('click', function() {
            handleCurrencyButtonClick(this, this.parentElement, false);
        });
    });

    // Запретить ввод отрицательных чисел
    const firstMoneyInput = document.getElementById("first_money");
    firstMoneyInput.addEventListener("input", function() {
       // const value = parseFloat(firstMoneyInput.value);

    });




    document.querySelector('.calculate').addEventListener('click', function(e) {
        e.preventDefault();

        if (firstCurrency && secondCurrency && firstMoneyInput.value) {

            const validPattern = /^-?\d+\.?\d*$/;
            if (!validPattern.test(firstMoneyInput.value)) {
                alert("Please enter a valid positive number.");
                return;
            }

            const amount = parseFloat(firstMoneyInput.value);
            

            if (isNaN(amount) || amount < 0) {
                alert("Please enter a valid positive number.");
                return;
            }

            if (firstCurrency === secondCurrency){
                alert("Please enter a different currecy.");
                return;
            }

            console.log(firstCurrency)

            fetch("/calculate_money", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    amount: amount,
                    from_currency: firstCurrency,
                    to_currency: secondCurrency
                })
            })
            .then(response => response.json())
            .then(data => {
                document.getElementById("last_money").value = data.output;
                //firstMoneyInput.value = "";  // Сброс значения первого поля
            })
            .catch(error => {
                console.error("Error:", error);
            });
        }
    });








    // Отправка данных на сервер для конвертации
    document.querySelector('.send').addEventListener('click', function(e) {
        e.preventDefault();

        if (firstCurrency && secondCurrency && firstMoneyInput.value) {

            const validPattern = /^-?\d+\.?\d*$/;
            if (!validPattern.test(firstMoneyInput.value)) {
                alert("Please enter a valid positive number.");
                return;
            }

            const amount = parseFloat(firstMoneyInput.value);
            

            if (isNaN(amount) || amount < 0) {
                alert("Please enter a valid positive number.");
                return;
            }

            if (firstCurrency === secondCurrency){
                alert("Please enter a different currecy.");
                return;
            }


            // AJAX-запрос на сервер Flask
            fetch("/convert_money", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    amount: amount,
                    from_currency: firstCurrency,
                    to_currency: secondCurrency
                })
            })
            .then(response => response.json())
            .then(data => {
                // Получаем результат с сервера и обновляем второе поле
                document.getElementById("last_money").value = data.get;
                firstMoneyInput.value = "0";  // Сброс значения первого поля
                if (data.get === 'success!'){
                    window.location.href = '/dashboard';
                }
            })
            .catch(error => {
                console.error("Error:", error);
            });
        }
    });
});