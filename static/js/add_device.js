Vue.createApp({
    data() {
      return {
        step: 0,
        group: "",
        name: "",
        loading: false,
        message: ""
      };
    },
    methods: {
      nextStep() {
        this.step = 1;
      },
      async sendConfiguration() {
        this.loading = true;
        try {
          const response = await fetch("/configure", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ grupo: this.group, name: this.name })
          });
          const data = await response.json();
          if (response.ok) {
            this.message = data.message || "Configuración enviada correctamente.";
            this.step = 2;
            // Redireccionar al dashboard después de un breve retraso para mostrar el mensaje y el loader
            setTimeout(() => {
              window.location.href = "/";
            }, 8000); // Espera 8 segundos
          } else {
            this.message = data.message || "Error en la configuración.";
            this.step = 2;
            this.loading = false; // Detener el loader en caso de error
          }
        } catch (error) {
          console.error("Error al enviar configuración:", error);
          this.message = "Error al enviar configuración.";
          this.step = 2;
          this.loading = false; // Detener el loader en caso de error
        }
      }
    }
  }).mount("#app");