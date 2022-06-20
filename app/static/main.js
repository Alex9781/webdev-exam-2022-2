'use strict';

var myModalEl = document.getElementById('delete-book-modal')
myModalEl.addEventListener('show.bs.modal', function (event) {
    let form = this.querySelector('form');
    form.action = event.relatedTarget.dataset.url;

    let userNameElement = document.getElementById('book-name');
    userNameElement.innerHTML = event.relatedTarget.closest('tr').querySelector('.book-title').textContent;
})