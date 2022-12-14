let user_account_update_inputs = document.querySelectorAll(
  ".user-account-update-input"
);
let upload_profile_picture = document.querySelector(".upload-profile-picture");
user_account_update_inputs = Array.from(user_account_update_inputs);
user_account_update_inputs = user_account_update_inputs.map((element) => [
  element,
  element.value,
]);
update_account_submit = document.querySelector(".update-account-submit");
update_account_submit.disabled = true;

user_account_update_inputs.forEach((user_account_update_input) => {
  user_account_update_input[0].addEventListener("input", (event) => {
    if (event.target.value != user_account_update_input[1]) {
      update_account_submit.disabled = false;
    } else {
      update_account_submit.disabled = true;
    }
  });
});

upload_profile_picture.addEventListener("change", (event) => {
  if (upload_profile_picture.value != "") {
    update_account_submit.disabled = false;
  }
});
