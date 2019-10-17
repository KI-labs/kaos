# encoding: utf-8
# copyright: 2018, The Authors

title "networking"
describe "Testing the networking module"

env = ENV["ENVIRONMENT"]

control 'TF Networks' do
  ## Assert that the Resource Group Exists
  describe azurerm_resource_groups do
      its('names') { should include "kaos-net-rg-#{env}" }
  end

  # Assert that the Vnet exists in the RG
  describe azurerm_virtual_networks(resource_group: "kaos-net-rg-#{env}") do
    it { should exist }
  end

  # Insist that Vnet exists
  describe azurerm_virtual_networks(resource_group: "kaos-net-rg-#{env}")
    .where(name: "kaos-vnet-#{env}") do
    it { should exist }
  end

  # Exists if any subnets exist for a given virtual network in the resource group
  describe azurerm_subnets(resource_group: 'kaos-net-rg-#{env}', vnet: "kaos-vnet-#{env}") do
    it { should exist }
  end

  # Insist that Subnet exists
  describe azurerm_subnets(resource_group: 'kaos-net-rg-#{env}', vnet: "kaos-vnet-#{env}")
    .where(name: "kaos-subnet-#{env}-0") do
    it { should exist }
  end
end