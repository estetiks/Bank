document.addEventListener("DOMContentLoaded", function() {
    let firstCurrency = null;
    let secondCurrency = null;

    // Функция для обработки нажатия кнопки валюты
    function handleCurrencyButtonClick(button, group, isFirstCurrency) {
        const buttons = group.querySelectorAll(".shares-btn-sell");
        buttons.forEach(btn => btn.classList.remove("active"));
        button.classList.add("active");

        if (isFirstCurrency) {
            firstCurrency = button.dataset.currency;
        } else {
            secondCurrency = button.dataset.currency;
        }

    
        
    }

    const firstCurrencyButtons = document.querySelectorAll('.currency-input:first-of-type .shares-btn-sell');
    firstCurrencyButtons.forEach(button => {
        button.addEventListener('click', function() {
            handleCurrencyButtonClick(this, this.parentElement, true);
        });
    });

    const secondCurrencyButtons = document.querySelectorAll('.currency-input:last-of-type .shares-btn-sell');
    secondCurrencyButtons.forEach(button => {
        button.addEventListener('click', function() {
            handleCurrencyButtonClick(this, this.parentElement, false);
        });
    });

    
    const sharesInput = document.getElementById("shares-sell");



    document.querySelector('.calculate-shares-sell').addEventListener('click', function(e) {
        e.preventDefault();


        if (firstCurrency && secondCurrency && sharesInput.value) {

            const validPattern = /^-?\d+$/;
            if (!validPattern.test(sharesInput.value)) {
                alert("Please enter a valid positive integer number.");
                return;
            }

            const amount = parseInt(sharesInput.value);
            

            if (isNaN(amount) || amount < 0) {
                alert("Please enter a valid positive int number.");
                return;
            }


            fetch("/calculate_shares", {
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
                document.getElementById("last_money_shares-sell").value = data.output;
            })
            .catch(error => {
                console.error("Error:", error);
            });
        }
    });








    // Отправка данных на сервер для конвертации
    document.querySelector('.convert-shares-sell').addEventListener('click', function(e) {
        e.preventDefault();

        if (firstCurrency && secondCurrency && sharesInput.value) {

            const validPattern = /^-?\d+$/;
            if (!validPattern.test(sharesInput.value)) {
                alert("Please enter a valid positive integer number.");
                return;
            }

            const amount = parseInt(sharesInput.value);
            

            if (isNaN(amount) || amount < 0) {
                alert("Please enter a valid positive integer number.");
                return;
            }



            // AJAX-запрос на сервер Flask
            fetch("/sell_shares", {
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
                document.getElementById("last_money_shares-sell").value = data.get;
                sharesInput.value = "0";  // Сброс значения первого поля
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