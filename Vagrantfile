# -*- mode: ruby -*-
# vi: set ft=ruby :

VAGRANTFILE_API_VERSION = "2"

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
  config.vm.provision "shell", path: "pg_config.sh"
 
 
  # config.vm.box = "hashicorp/precise32"
  config.vm.box = "ubuntu/trusty32"
  config.vm.network "forwarded_port", guest: 7000, host: 7000
  config.vm.network "forwarded_port", guest: 9000, host: 9000
end
