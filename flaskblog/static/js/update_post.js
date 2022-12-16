let user_post_update_inputs = document.querySelectorAll(
  ".user-post-update-input"
);

user_post_update_inputs = Array.from(user_post_update_inputs);
user_post_update_inputs = user_post_update_inputs.map((element) => [
  element,
  element.value,
]);
update_post_submit = document.querySelector(".update-post-submit");
update_post_submit.disabled = true;

user_post_update_inputs.forEach((user_post_update_input) => {
  user_post_update_input[0].addEventListener("input", (event) => {
    if (event.target.value != user_post_update_input[1]) {
      update_post_submit.disabled = false;
    } else {
      update_post_submit.disabled = true;
    }
  });
});
