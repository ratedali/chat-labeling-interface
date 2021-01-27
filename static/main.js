$(function () {
  const categoryInputs = $('input[type="radio"][name="category"]');
  const categories = categoryInputs.map((_, input) => $(input).attr('value'))
  const subcategories = new Map();
  categories.each((i, category) => {
    subcategories.set(category,
      $(`#${category} options`).map((_, option) => $(option).attr('value')),
    );
  });

  categoryInputs.change(function () {
    categories.each((i, category) => {
      if (category == this.value) {
        $(`#${category}`).removeClass('d-none');
      } else {
        $(`#${category}`).addClass('d-none');
      }
    });
  });
});