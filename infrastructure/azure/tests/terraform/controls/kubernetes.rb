# encoding: utf-8
# copyright: 2018, The Authors

title "Kubernetes"
describe "Testing the K8s module"

env = ENV["ENVIRONMENT"]

control 'TF Kubernetes' do
    ## Assert that the Resource Group Exists
  describe azurerm_resource_groups do
    its('names') { should include "k8s-#{env}" }
  end

  ### Test that a Resource Group has the named AKS Cluster
  describe azurerm_aks_clusters(resource_group: "k8s-#{env}") do
    its('names') { should include("k8s-#{env}") }
  end

  # Insist that Vnet exists
  describe azurerm_virtual_networks(resource_group: "k8s-#{env}")
    .where(name: 'kaos-vnet-dev') do
    it { should exist }
  end

  # Insist that MySubnet exists
  describe azurerm_subnets(resource_group: "k8s-#{env}", vnet: "kaos-vnet-#{env}")
    .where(name: "k8s-subnet-#{env}") do
    it { should exist }
  end
end
