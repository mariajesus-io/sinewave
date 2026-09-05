import re

with open('/home/maria/sinewave/tienda/templates/registro.html', 'r') as f:
    content = f.read()

new_js = """{% block extra_js %}
<script>
  document
    .getElementById("registroForm")
    .addEventListener("submit", function (e) {
      e.preventDefault();
      const form = e.target;
      if (!form.checkValidity()) {
        e.stopPropagation();
        form.classList.add('was-validated');
        return;
      }
      
      const msg = document.getElementById("error-msg");
      const email = document.getElementById("email").value;
      const pass = document.getElementById("contrasena").value;
      const pass2 = document.getElementById("contrasena2").value;
      const nombre = document.getElementById("nombre").value;

      if (pass !== pass2) {
        msg.textContent = "Las contraseñas no coinciden.";
        msg.classList.remove("d-none");
        return;
      }
      if (pass.length < 6) {
        msg.textContent = "La contraseña debe tener al menos 6 caracteres.";
        msg.classList.remove("d-none");
        return;
      }
      
      let users = JSON.parse(localStorage.getItem('sinewave_users')) || [];
      // Check if user already exists
      if (users.find(u => u.email === email) || email === "admin@sinewave.cl") {
        msg.textContent = "Ya existe una cuenta con este correo electrónico.";
        msg.classList.remove("d-none");
        return;
      }
      
      users.push({
        nombre: nombre,
        email: email,
        pass: pass
      });
      localStorage.setItem('sinewave_users', JSON.stringify(users));
      
      msg.classList.add("d-none");
      alert("¡Registro exitoso! Ahora puedes iniciar sesión.");
      window.location.href = "{% url 'login' %}";
    });
</script>
{% endblock %}"""

content = re.sub(r'{% block extra_js %}.*?{% endblock %}', new_js, content, flags=re.DOTALL)

with open('/home/maria/sinewave/tienda/templates/registro.html', 'w') as f:
    f.write(content)

print("Registro JS updated")
