# Explicación Tarea 6

## Santiago Muñoz Venezian; santi95

21 de Noviembre, 2017

Para que sea más facil de corregir, lo que no me funcionó fue:

    1. El Balde
    2. Al hacer un blurry, si esque hay espectadores el cliente 
        editando hace el blurry 2 veces, la razón se explicará más 
        adelante.
    3. al hacer <> en los emojis, estos se muestran igual, me faltó 
        tiempo
    4. Solamente los clientes detectan que salió un usuario cuando usa el botón
        salir del editor.

Todo el resto funciona super bien en general

Mi tarea tiene 9 archivos, de los cuales varios son de Designer,
 pero se explicarán solamente los de python

    1. Servidor:
        a. Func_photo.py
        b. Server2.py  #Mi server1 era un desastre jajaj
    2. Cliente:
        a. FrontEnd.py
        b. BackEnd.py
        c. Client2.py  #Adivina que pasaba con el cLiente1

#### General

Creo importante explicar previamente el funcionamiento de mi tarea. Siento que 
la idea era minimizar los datos traspasados desde el servidor a los clientes. 
Por lo tanto en mi programa, cuando un usuario que está editando una foto 
realiza un cambio, le avisa al servidor para que el servidor haga un cambio en 
la foto original y además le avisa a todos los espectadores que se hizo el 
cambio. En blurry, el servidor le dice a cada uno de los espectadores que el 
cliente realice el blurry por su cuenta, el servidor no le manda los bytes 
nuevos de la foto.



#### 1.Func_photo.py

    Es basicamente una copia del BackEnd del cliente, solamente que cambia las 
    fotos originales. 

    Tiene una clase Foto, que recibe los parametros necesarios para 
    hacer los cambios que el servidor le pide en las fotos de la 
    carpeta "image"

    Tiene 5 funciones:
        1. get_rgb: Toma el nombre de la imagen a cambiar, y retorna 
        la matriz rgb
        2 blurry_be: El nombre viene de blurry backend, 
        originalísimo. Lee todos los pixeles de la matriz antes 
        generada y cambia los valores de todos los pixeles.
        3. reamar_foto: Toma el idat nuevo recién generado por alguno 
        de los efectos y sobreescribe la foto en la carpeta original.
        4. hacer_blurry: Llama a las funciones necesarias en el 
        backend, en el orden deseado para que se haga el blurry.
        5. recortar: funciona muy parecido al hacer_blurry, llama a 
        las funciones para completar el trabajo, parecido a lo que 
        hace un gerente.

#### 2. Server

    El Host y el port están visibles pero al final! Siempre tuve la intención
    de moverlos, pero hice el último commit muy a la rápida, ya que a las 11pm
    del día de la entrega todo me falló en el programa.

    Me imagino que debes estar corrigiendo 2543 servers iguales, todos basados 
    en el de los contenidos, asique te voy a explicar solamente la diferencia 
    del mio con el basal.

    Encuentre las 5 diferencias:
        1. En el init creo los diccionarios que voy a usar en el 
        resto del servidor, sus funciones están explicadas con #s 
        arriba de cada uno de ellos.
        2. Mi send tiene unas ediciones, todo contenido mandado tiene 
        la siguiente estructura.

        (largo_del_body_en_bytes + 5bytes que nos dicen el tipo de 
            mensaje enviado + el body en pickle)

        2. De esta forma, cuando el cliente recibe el mensaje, primero 
        descompone los primeros 4 bytes para saber el largo extra que 
        tiene que recibir, luego saca los siguientes 5 bytes que nos 
        dicen como se va a manejar este mensaje con un "tipo" y 
        finalmente tiene lo que se quiso mandar serializado con
        pickle.

        3. El listen manejaba solamente los tipos 'verif' que los recibe el 
        servidor cuando el cliente está intentando autenticar el nombre
        de usuario, el resto de los tipos de mensaje se van al handlecommand, 
        que maneja una cantidad mayor de tipos de mensajes recibidos.

        4. Los tipos de mensajes elegí que fueran de 5bytes, por eso tienen 
        nombres tan extraños. Hay varios prints que se me fue borrar antes del 
        último commit, por ejemplo "Este es el que te fijas" eso iba para mi, 
        no para ti jaja. La tónica es que todos reciben un tipo de mensaje, que 
        socket se los mando y el mensaje en sí y pueden tanto devolver algo
        al cliente como no. 

        5. Algunos tipos como el dicti simplementen le dicen al servidor que 
        agregue al usuario a la lista de espectadores, para que le empiecen a 
        llegar los cambios que el editor está haciendo en vivo. Este lista de 
        espectadores, es la misma que los que están chateando en esa foto, por 
        lo tanto, el editor está dentro de la lista de espectadores y por eso
        hace blurry 2 veces, no llegué a hacer ese cambio. Igual 1 blurry era 
        poco cambio dicen los picados.

#### 3. FrontEnd

    1. CLase Login, bueno, hace el login.

        Jajajaj, Le pregunta al servidor via el cliente si es que hay otro 
        usuario con ese mismo nombre, si no lo hay y cumple las demás razones, lo deja entrar. Además crea el cliente y muestra el dashboard

    2. Clase PopUp, levanta una ventanita diciendo que el usuario no es válido

    3. Clase Dashboard, está muy desordenada e ineficiente, pero funciona 
        super. Existe el metodo del módulo cliente salir() con el cual le dice 
        al servidor que alguien salió y lo actualiza en el dashboard, pero 
        con los cambios de ventanas eso me complicó y decidí dejarlo 
        implementado, pero no aplicado. Cuando ingresa un usuario nuevo, si
        actualiza los usuarios conectados. 

        a. Pide las fotos
        b. Conecta los triggers del cliente
        c. Espera ciclos de 0.7 segundos hasta que llegan las fotos desde el 
            servidor. Ese tiempo podría ser menos
        d. Crea los pixmaps como iconos de botones, así no pierden el ratio
            y son apretables sin problemas extras.
        e. Espera a que llegue la información de cuales fotos están siendo
            editadas ahora. Pone los tags de disponible o ocupado. LA función
            recibir dicti ocupados, podría ser usada en el init, está copiada. 
            Esto es así porque a veces me tiraba error cuando las fotos llegaban
            después del estado de las fotos.
        f. Marca las condiciones de entrada a cada una de las fotos, le dice al
            usuario si esque entra como editor o espectador.

    4. Editor, tiene unos cuantos triggers, hace los mousepressevent, para ver
        la posición en la cual se apretó la foto. Le da funcionalidades 
        distintas a los usuarios dependiendo de si son espectadores o Editores, 
        pero esto no se muestra más que con un label Espectador arriba.

        a. blurry_remoto: hace que el cliente del espectador haga un blurry 
            sobre su foto. Este es el que hace que el del editor se haga 2 
            veces. Se hace a través de un trigger
        b. recorte_remoto: lo mismo que el anterior, solo que cuando un corte
            se hace 2 veces no se nota... Se llega a través de un trigger del 
            cliente.Tal vez no debería estar escribiendo eso. Es facil de arreglar eso si, solo hay que hacer una copia de la lista en el servidor y funcionaría. Me falta nota para pasaaaar :((((
        c. poner_comentarios_nuevos. Adivinaste, actualiza los comentarios 
            nuevos en vivo dentro de los espectadores y cada vez que alguien 
            entra de espectador.
        d. blurry_fe: le pide al backend que haga el blurry. Le dice al servidor
            que un blurry se hizo y en que foto, para que avise. A los 
            espectadores le dice que lo hagan sus propios clientes, además, 
            se le realiza a la imagen original.
        e. descargar_imagen: Adivinaste de nuevo!! descarga la imagen en el 
            directorio actual.
        f. agregar_comentario pone los emojis de la carpeta y se los manda al 
            servidor. 
        g. armar_foto es una redundancia del backend
        h. recortando: le dice a los clicks que desde ese minuto importan.
        i. click: si es que se apreta con el modo recortando, guarda su 
            posición.
        j. release: si es está en modo recortando, saca el modo y le dice al
            backend que haga el recortar, ese if del final es redundante, 
            pero le pide al cliente que mande los cambios al servidor
            y así le diga a los espectadores que hagan el cambio, via el
            recorte_remoto.
        k. salir: cuando se usa este botón salir los dashboards de los demás,
        reconocen que alguien se salió.

#### 4. BackEnd

    Muy parecido al Func_photo del servidor, pero trabaja todo en bytes, creo 
    que no vale la pena explicarlo denuevo, ya va muy largo el readme, sorry
    por eso.

#### 5. Cliente, mi parte favorita. El junior del programa.
    
    Tiene lo mismo que casi todos los clientes, pero mandan y recibe mensajes
    de la misma forma que lo hace el servidor, largo mensaje, tipo, mensaje.

    Partiré explicandolo de abajo para arriba. Abajo se ven las funciones que
    llama el FrontEnd. Envía usuarios, mensajes, que marque fotos ocupadas, 
    nuevo usuario, nuevo comentario, agrega y saca espectadores, pide fotos,
    pide usuarios conectados, lo mandan a hacer todos los cachos. Algunos
    mensaje solamente necesitan el tiempo, como por ejemplo salir. Por lo tanto,
    el mensaje es "nada". 

    Luego un poco más arriba se ven los triggers, los que generan cambios, a 
    partir de mensajes recibidos por el cliente desde el servidor. 

    Haré una sección de anexos al final explicando todos los tipos de mensajes, 
    leelos solo si tienes tiempo y te podrían ayudar a corregir la tarea.

--------------------------------------------------------------------------------

Muy entretenida la Tarea! Espero que este ReadMe te haga la corrección más 
amena con este fin de semestre.
Entretenida la Tarea!! Quedé con ganas de hacer el balde. Una idea para esta 
tarea el próximo semestre podría ser hackearse el server desde otro computador.

Gracias por corregirmela!!! :D

