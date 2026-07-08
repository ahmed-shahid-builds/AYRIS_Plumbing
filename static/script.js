/* JAKE'S PLUMBING WEBSITE JAVASCRIPT */

/*SMOOTH SCROLL BUTTONS*/


const buttons =
document.querySelectorAll("a[href^='#']");



buttons.forEach(button=>{


    button.addEventListener(
    "click",
    function(e){


        const target =
        document.querySelector(
        this.getAttribute("href")
        );



        if(target){


            e.preventDefault();


            target.scrollIntoView({

                behavior:"smooth"

            });


        }


    });


});









/* SIMPLE IMAGE HOVER EFFECT */


const images =
document.querySelectorAll(".service-card img");



images.forEach(img=>{


    img.addEventListener(
    "mouseenter",
    ()=>{


        img.style.filter =
        "brightness(85%)";


    });



    img.addEventListener(
    "mouseleave",
    ()=>{


        img.style.filter =
        "brightness(100%)";


    });



});









/* BOOKING FORM SUBMISSION (with Cloudflare Turnstile token) */


const bookingForm =
document.querySelector("#booking-form");


const bookingStatus =
document.querySelector("#booking-status");



/* SAFE STATUS RENDERER
    Always writes with textContent (never innerHTML), so even if a
    malicious or unexpected string comes back from the server, it is
    displayed as plain visible text and can never execute as HTML/JS.*/
function renderBookingStatus(message, isError){


    if(!bookingStatus){


        return;


    }


    bookingStatus.textContent =
    String(message);


    bookingStatus.classList.remove(
    "status-success",
    "status-error"
    );


    bookingStatus.classList.add(
    isError ? "status-error" : "status-success"
    );


}



if(bookingForm){


    bookingForm.addEventListener(
    "submit",
    function(e){


        e.preventDefault();


        const turnstileToken =
        bookingForm.querySelector(
        "[name='cf-turnstile-response']"
        )?.value;



        if(!turnstileToken){


            renderBookingStatus(
            "Please complete the verification challenge before submitting.",
            true
            );


            return;


        }



        const payload = {

            name: bookingForm.querySelector("[name='name']").value,
            phone: bookingForm.querySelector("[name='phone']").value,
            time: bookingForm.querySelector("[name='time']").value,
            service: bookingForm.querySelector("[name='service']").value,
            address: bookingForm.querySelector("[name='Address']").value,
            "cf-turnstile-response": turnstileToken

        };



        renderBookingStatus(
        "Submitting your appointment…",
        false
        );



        fetch(
        bookingForm.action,
        {

            method:"POST",

            headers:{
                "Content-Type":"application/json"
            },

            body: JSON.stringify(payload)

        })
        .then(response=>{


            if(!response.ok){


                throw new Error("Booking request failed");


            }


            return response.json().catch(()=>({}));


        })
        .then(data=>{


            /* data.message (if the backend sends one) is rendered with
                textContent only — never innerHTML — so it cannot be used
                to inject a script tag or event handler into the page.*/
            const confirmationText =
            (data && typeof data.message === "string" && data.message.trim())
            ? data.message
            : "Appointment reserved! We'll confirm by phone shortly.";


            renderBookingStatus(
            confirmationText,
            false
            );


            setTimeout(
            ()=>{ window.location.reload(); },
            1500
            );


        })
        .catch(error=>{


            console.error("Booking submission error:", error);


            renderBookingStatus(
            "Something went wrong submitting your appointment. Please try again.",
            true
            );


        });


    });


}
