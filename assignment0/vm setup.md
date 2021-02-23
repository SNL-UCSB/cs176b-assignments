# Virtual Machine Setup

Please follow the instructions below to set up your virtual machine (VM). Setttip up this VM, will make it easy to install all dependencies for the programming assignments, saving you the tedium of installing individual packages and ensuring your development environment is correct.

## Step 1 : Install Vagrant

Vagrant is a tool for automatically configuring a VM using instructions given in a single "Vagrantfile."

**macOS & Windows:** You need to install Vagrant using the correct download link for your computer here: <https://www.vagrantup.com/downloads.html>.

**Windows only**: You will be asked to restart your computer at the end of the installation. Click Yes to do so right away, or restart manually later, but don't forget to do so or Vagrant will not work!

**Linux:** First, make sure your package installer is up to date by running the
command `sudo apt-get update`. To install Vagrant, you must have the "Universe"
repository on your computer; run `sudo apt-add-repository universe` to add it.
Finally, run `sudo apt-get install vagrant` to install vagrant.

## Step 2: Install VirtualBox

VirtualBox is a VM provider (hypervisor).

**macOS & Windows:** You need to install VirtualBox using the correct download
link for your computer here: <https://www.virtualbox.org/wiki/Downloads>. The
links are under the heading "VirtualBox 6.x.x platform packages."

**Note**: If you encounter the `installation failed` issue, then follow the instructions [here](https://osxdaily.com/2018/12/31/install-run-virtualbox-macos-install-kernel-fails/) to install virtual box.

**Windows only:** Use all the default installation settings.

**Linux:** Run the command `sudo apt-get install virtualbox`.

**Note:** This will also install the VirtualBox application on your computer,
but you should never need to run it, though it may be helpful (see Step 6).

## Step 3: Install Git (and SSH-capable terminal on Windows)

Git is a distributed version control system.

**macOS & Windows:** You need to install Git using the correct download link
for your computer here: <https://git-scm.com/downloads>.

**macOS only:** Once you have opened the .dmg installation file, you will see a
Finder window including a .pkg file, which is the installer. Opening this
normally may give you a prompt saying it can't be opened because it is from an
unidentified developer. To override this protection, instead right-click on
thet .pkg file and select "Open". This will show a prompt asking you if you are
sure you want to open it. Select "Yes". This will take you to the
(straightforward) installation.

**Windows only:** You will be given many options to choose from during the
installation; using all the defaults will be sufficient for this course (you
can uncheck "View release notes" at the end).  

You should also download PuTTY from <https://www.chiark.greenend.org.uk/~sgtatham/putty/latest.html> to ssh into your VM.

**Linux:** `sudo apt-get install git`

## Step 4: Install X Server

You will need an X Server to input commands to the virtual machine.

**macOS:** Install [XQuartz](https://www.xquartz.org/). You will need to log
out and log back in to complete the installation (as mentioned by the prompt at
the end).

**Windows:** Install
[Xming](https://sourceforge.net/projects/xming/files/Xming/6.9.0.31/Xming-6-9-0-31-setup.exe/download).
Use default options and uncheck "Launch Xming" at the end.

**Linux:** The X server is pre-installed!

## Step 5: Clone course Git repository

Open your terminal (use git bash if using Windows) and `cd`
to wherever you want to keep files for this course on your computer.  

Run `git clone https://github.com/agupta13/cs176b-assignments.git` to
download the course files from GitHub.

`cd cs176b-assignments/` to enter the course assignment directory.

## Step 6: Provision virtual machine using Vagrant

`cd cs176b-assignments/vm` directory, run the command  `vagrant
up` to start the VM and provision it according to the Vagrantfile. You will
likely have to wait for at least an hour.

**Note 1**: The following commands will allow you to stop the VM at any point
(such as when you are done working on an assignment for the day):

* `vagrant suspend` will save the state of the VM and stop it.
* `vagrant halt` will gracefully shutdown the VM operating system and power
  down the VM.
* `vagrant destroy` will remove all traces of the VM from your system. If you
  have important files saved on the VM (like your assignment solutions) **DO
  NOT** use this command.

Additionally, the command `vagrant status` will allow you to check the status
of your machine in case you are unsure (e.g. running, powered off, saved...).
You must be in some subdirectory of the directory containing the Vagrantfile to
use any of the commands above, otherwise Vagrant will not know which VM you are
referring to.

**Note 2**: The VirtualBox application that was installed in Step 2 provides a
visual interface as an alternative to these commands, where you can see the
status of your VM and power it on/off or save its state. It is not recommended
to use it, however, since it is not integrated with Vagrant, and typing
commands should be no slower. It is also not an alternative to the initial
`vagrant up` since this creates the VM.

## Step 7: Test SSH to VM

**macOS & Linux:**
Run `vagrant ssh` from your terminal. This is the command you will use every
time you want to access the VM. If it works, your terminal prompt will change
to `vagrant@host:~$`.

The command `logout` will stop the SSH connection at any point. If prompted, the username is `p4` and password is also `p4`

**Windows Only**:
The built-in power shell ssh is a bit limited, you may use PuTTY to ssh into your VM. Put `127.0.0.1` as your host name, and `2222` as port. Tick `Enable X11 Forwarding` under `Connection-SSH-X11`, then go to `Connection-SSH-Auth` and browse your private key created at `cs176b-assignments\.vagrant\machines\default\virtualbox\private_key` (remember to allow all file types to be the input when browsing).

Lastly, please test if the X11 Forwarding is configured correctly, run `chromium-browser` in the PuTTY terminal, and chromium should be rendered in your host OS.

## Extra Note for Windows users

Line endings are symbolized differently in DOS (Windows) and Unix
(Linux/MacOS). In the former, they are represented by a carriage return and
line feed (CRLF, or "\r\n"), and in the latter, just a line feed (LF, or "\n").
Given that you ran `git pull` from Windows, git detects your operating system
and adds carriage returns to files when downloading. This can lead to parsing
problems within the VM, which runs Ubuntu (Unix). Fortunately, this only seems
to affect the shell scripts (\*.sh files) we wrote for testing. The
`Vagrantfile` is set to automically convert all files back to Unix format, so
**you shouldn't have to worry about this**. **However**, if you want to
write/edit shell scripts to help yourself with testing, or if you encounter
this problem with some other type of file, use the preinstalled program
`dos2unix`. Run `dos2unix [file]` to convert it to Unix format (before
editing/running in VM), and run `unix2dos [file]` to convert it to DOS format
(before editing on Windows). A good hint that you need to do this when running
from the VM is some error message involving `^M` (carriage return). A good hint
you need to do this when editing on Windows is the lack of new lines. Remember,
doing this should only be necessary if you want to edit shell scripts.

## Step 8: Go take a break. You've earned it

## Q&A

* **I'm getting an error when I run the command `vagrant up`. What do I do?**
  Many errors/warnings are not a problem and do not need to be addressed, such
  as `==> default: stdin: is not a tty`. Usually, errors starting with `==>
  default` should not be worried about, but others should, in particular if
  they cause the process to be aborted. Use `vagrant status` to see if the VM
  is running after `vagrant up`; if it is not, then there is a real problem.
  Here are some known errors and how to fix them:
  * **"A Vagrant environment or target machine is required to run this
      command..."**: you must run `vagrant up` from a subdirectory of the
      directory containing the Vagrantfile (in the case, `assignments`).
    * **"Vagrant cannot forward the specified ports on this VM, since they
      would collide with some other application that is already listening on
      these ports..."**: perhaps you cloned the repository twice and the VM is
      already running on one of them. Since they both use the same port, they
      cannot run at the same time. You may also have some other application
      using port 2222. To help find what is using it, follow
      [these](http://osxdaily.com/2014/05/20/port-scanner-mac-network-utility/)
      instructions for macOS,
      [these](https://techtalk.gfi.com/scan-open-ports-in-windows-a-quick-guide/)
      for Windows and
      [these](https://wiki.archlinux.org/index.php/Nmap#Port_scan) for Linux
      (you may have to install `nmap`). Use 127.0.0.1 as the IP and 2222-2222
      as the port range in your port scan.

  If this did not help you fix the problem, please ask on Piazza or at office
  hours.
