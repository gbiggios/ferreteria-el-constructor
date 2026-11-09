// Avisos flotantes (toast) de django.contrib.messages.
// - La X cierra el aviso.
// - Si el aviso tiene barra de tiempo (éxito / info), se cierra solo cuando la barra termina (5 s).
//   La pausa al pasar el mouse la hace el CSS (animation-play-state), así barra y cierre van sincronizados.
document.querySelectorAll('.mensaje').forEach(function (mensaje) {
    function cerrar() {
        if (mensaje.classList.contains('mensaje-saliendo')) return;
        mensaje.classList.add('mensaje-saliendo');
        // animationend también llega "burbujeando" desde la barra de tiempo: solo cuenta la salida del propio aviso
        mensaje.addEventListener('animationend', function (e) {
            if (e.target === mensaje) mensaje.remove();
        });
    }

    mensaje.querySelector('.mensaje-cerrar').addEventListener('click', cerrar);

    var tiempo = mensaje.querySelector('.mensaje-tiempo');
    if (tiempo) {
        tiempo.addEventListener('animationend', cerrar);
    }
});
