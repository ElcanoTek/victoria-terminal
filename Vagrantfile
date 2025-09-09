# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|

  # Prevent automatic box updates, which can be disruptive.
  config.vm.box_check_update = false

  # Common settings for all VMs
  config.vm.provider "virtualbox" do |vb|
    vb.memory = "4096"
    vb.cpus = "2"
  end

  # Define the Windows 11 testing machine
  config.vm.define "windows11" do |win|
    win.vm.box = "bento/windows-11"
    win.vm.communicator = "winrm"

    # Enable the GUI for manual testing
    win.vm.provider "virtualbox" do |vb|
      vb.gui = true
    end

    # Provision with a PowerShell script to run the installer
    win.vm.provision "shell", path: "tests/provision_win.ps1"
  end

  # Define the Ubuntu testing machine
  config.vm.define "ubuntu" do |ubu|
    ubu.vm.box = "ubuntu/jammy64" # Ubuntu 22.04 LTS

    # Enable the GUI for manual testing
    ubu.vm.provider "virtualbox" do |vb|
      vb.gui = true
    end

    # Provision the VM
    ubu.vm.provision "shell", inline: <<-SHELL
      echo "Installing Ubuntu Desktop..."
      # Update package list
      sudo apt-get update -y
      # Install the full desktop environment. This will take some time.
      # Using DEBIAN_FRONTEND=noninteractive to prevent it from asking questions during installation.
      sudo DEBIAN_FRONTEND=noninteractive apt-get install -y ubuntu-desktop^
      echo "Ubuntu Desktop installed."
    SHELL

    # Run the application setup script
    ubu.vm.provision "shell", path: "tests/provision_ubuntu.sh"
  end

end
