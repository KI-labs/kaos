# frozen_string_literal: true

require 'awspec'
Awsecrets.load(secrets_path: File.expand_path('./secrets.yml', File.dirname(__FILE__)))


describe security_group('kaos-2-test-all-worker-management') do
   it { should exist }
   it { should belong_to_vpc('kaos-2-test-vpc') }
   it { should_not be_inbound_opened_only }
   it { should be_outbound_opened_only }
   it { should have_tag('project').value('kaos') }
   it { should have_tag('env').value('test') }
   it { should have_tag('version').value('2') }
   its(:inbound) { should be_opened(22).protocol('tcp').for('10.0.0.0/8') }
end

describe security_group('kaos-2-test-worker-group-mgmt-one') do
   it { should exist }
   it { should belong_to_vpc('kaos-2-test-vpc') }
   it { should_not be_inbound_opened_only }
   it { should be_outbound_opened_only }
   it { should have_tag('project').value('kaos') }
   it { should have_tag('env').value('test') }
   it { should have_tag('version').value('2') }
   its(:inbound) { should be_opened(22).protocol('tcp') }
end

describe security_group('kaos-2-test-worker-group-mgmt-two') do
   it { should exist }
   it { should belong_to_vpc('kaos-2-test-vpc') }
   it { should_not be_inbound_opened_only }
   it { should be_outbound_opened_only }
   it { should have_tag('project').value('kaos') }
   it { should have_tag('env').value('test') }
   it { should have_tag('version').value('2') }
   its(:inbound) { should be_opened(22).protocol('tcp').for('192.168.0.0/16') }
end