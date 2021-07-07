from flask import Flask, render_template
from flask import request
from flask.sessions import NullSession
import virtualbox
from virtualbox.library import NetworkAttachmentType
from virtualbox.library import LockType
app=Flask(__name__)
#virtual box
vbox = virtualbox.VirtualBox()
#landing page
@app.route('/')
def index():
    return render_template("index.html")

#afficher la liste des machine
@app.route('/afficher',methods=['POST','GET'])
def afficher_machine():
    
    machine=[] #pour creer une table pour l'envoyer à machine.html
    for m in vbox.machines:
         machine.append(m.name)
    return render_template("machine.html",data=machine)

#afficher la liste des machine en execution
@app.route('/execution',methods=['POST','GET'])
def afficher_machine_execution():
   
    machine =[]
    for m in vbox.machines:
         if m.state!=1: # les machines qui ont en execution donc le state!=1
             machine.append(m.name)
                   
    return render_template("machine.html",data=machine)
#lancer une machine
@app.route('/lancer',methods=['POST','GET'])
def lancer_machine():
    session = virtualbox.Session()
    nom=request.form.get('nom')
    machine = vbox.find_machine(nom)  ## for example: "ubuntu"
    # If you want to run it normally:
    proc = machine.launch_vm_process(session, "gui",[])
    # If you want to run it in background:
    # proc = machine.launch_vm_process(session, "headless")
    proc.wait_for_completion()
    return render_template("index.html")

#arreter la machine
@app.route('/arreter',methods=['POST','GET'])
def arreter_machine():
    nom=request.form.get('nom')
    machine = vbox.find_machine(nom) 
    session=machine.create_session()
    session.console.power_down()
    return render_template("index.html")

#afficher les adresse ip
@app.route('/ipadresse',methods=['POST','GET'])
def afficher_adresse():
    session = virtualbox.Session()
    nom=request.form.get('nom')
    mgr = virtualbox.Manager(None, None)
    vbox = mgr.get_virtualbox()
    vm = vbox.find_machine(nom)
    liste=vm.enumerate_guest_properties("/VirtualBox/GuestInfo/Net/*/V4/IP") #c'est pour récupérer les adresse ip de tous les adapters
    adresse =[]
    i=0
    for m in liste:
        adresse.append(liste[i])
        i=i+1
    return render_template("machine.html",data=adresse)
    #configurer une machine
@app.route('/configurer',methods=['POST','GET'])
def configurer_machine():
    return render_template("configurer.html")


@app.route('/configurer_machine',methods=['POST'])
def get_form_data():
    
    machine_name=request.form.get('name_machine')
    memoryS=request.form.get('memory_size')
    cpuC=request.form.get('cpu_count')
    nom=request.form.get('nom')
    #changer les paramètres
    vboxmanager = virtualbox.Manager()
    vbox = vboxmanager.get_virtualbox()
    session = vboxmanager.get_session()
    vm = vbox.find_machine(machine_name)
    if vm==NullSession : message=" pas de machine avec ce nom" #dans le cas d'erreur
    rc = vm.lock_machine(session,LockType.write) #pour qu'il permet de chnager les paramètres
    #changer la taille
    session.machine.memory_size=int(memoryS)
    #changer le nombre des cpu
    session.machine.cpu_count=int(cpuC)
    #changer le  nom
    session.machine.name=nom
    #save changes
    session.machine.save_settings()
    message="La configuration a été bien établi"
    return render_template("configurer.html",data=message)
#configurer les cartes réseaux
@app.route('/configurercarte',methods = ["GET","POST"])
def returnpage():
    return render_template("upload.html")

@app.route('/configurer2',methods = ["GET","POST"])
def home():

   if request.method == "POST":
      
      """Creates a new appliance object, which represents an appliance in the Open Virtual Machine
        Format (OVA). This can then be used to import an OVF appliance into VirtualBox
        """
      appareil_virt = vbox.create_appliance()

      "Reads an OVF file into the appliance object."
      appareil_virt.read(request.form["path"])

      "This line will need the name of the appliance to import."
      description = appareil_virt.find_description(request.form["ova_name"])

      "This instruction will set the name of the created the machine"
      description.set_name(request.form["name"])

      "This instruction will set the cpu of the created machine"
      description.set_cpu("2")

      "Imports the appliance into VirtualBox to create the machine"
      p = appareil_virt.import_machines()

      "This instruction will wait for the completion of the creatung machine process"
      p.wait_for_completion()
      return render_template("upload.html")
   else:
      return render_template("upload.html")

#configurer network adapter
@app.route('/network',methods = ["GET","POST"])
def network():
    machine = vbox.find_machine('ubuntu') #par exemple le nom de la machine = ubuntu
    with machine.create_session() as session:
        adapter = session.machine.get_network_adapter(0)
        adapter.enabled = True
        adapter.attachment_type = NetworkAttachmentType.bridged
        session.machine.save_settings()
    return render_template("index.html")
app.run(host="127.0.0.1",port=6120)