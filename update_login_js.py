import re

with open('/home/maria/sinewave/tienda/templates/login.html', 'r') as f:
    content = f.read()

new_js = """{% block extra_js %}
<script>
  document
    .getElementById("loginForm")
    .addEventListener("submit", function (e) {
      e.preventDefault();
      const form = e.target;
      if (!form.checkValidity()) {
        e.stopPropagation();
        form.classList.add('was-validated');
        return;
      }
      
      const email = document.getElementById("email").value;
      const pass = document.getElementById("contrasena").value;
      const errorMsg = document.getElementById("error-msg");

      if (email === "admin@sinewave.cl" && pass === "admin123") {
        window.location.href = "/admin/";
        return;
      }
      
      let users = JSON.parse(localStorage.getItem('sinewave_users')) || [];
      let foundUser = users.find(u => u.email === email);
      
      if (!foundUser) {
        errorMsg.innerHTML = 'No existe una cuenta con este correo. Por favor, <a href="{% url 'registro' %}">crea una cuenta nueva aquí</a>.';
        errorMsg.classList.remove('d-none');
        return;
      }
      
      if (foundUser.pass !== pass) {
        errorMsg.textContent = 'Contraseña incorrecta. Por favor, intenta de nuevo.';
        errorMsg.classList.remove('d-none');
        return;
      }
      
      errorMsg.classList.add('d-none');
      window.location.href = "{% url 'checkout' %}";
    });
</script>
{% endblock %}"""

content = re.sub(r'{% block extra_js %}.*?{% endblock %}', new_js, content, flags=re.DOTALL)

with open('/home/maria/sinewave/tienda/templates/login.html', 'w') as f:
    f.write(content)

print("Login JS updated")
