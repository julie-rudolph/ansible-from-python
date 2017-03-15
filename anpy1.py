#!/usr/bin/python
# in git branch dev

from collections import namedtuple
from ansible.parsing.dataloader import DataLoader
from ansible.vars import VariableManager
from ansible.inventory import Inventory
from ansible.playbook.play import Play
from ansible.executor.task_queue_manager import TaskQueueManager
from ansible.plugins.callback import CallbackBase
import json

global hostresults
hostresults = {}

class ResultCallback(CallbackBase):
	def v2_runner_on_ok(self, result, **kwargs):
		theresult = result._host
		print json.dumps({theresult.name: result._result}, indent=4)
		self.hostresults = json.dumps({theresult.name: result._result})
		print type(self.hostresults)


Options = namedtuple('Options',
                ['connection', 'module_path', 'forks', 'become',
                 'become_method', 'become_user', 'check']
            )

variable_manager = VariableManager()
loader = DataLoader()

#options = Options(
#    connection='local', module_path='', forks=100, become=True,
#    become_method='sudo', become_user='root', check=False)

options = Options(
    connection='local', module_path='', forks=100, become=False,
    become_method='', become_user='root', check=False)

inventory = Inventory(loader=loader, variable_manager=variable_manager,
                      host_list='inthosts.txt')

passwords = dict(vault_pass='secret')

variable_manager.set_inventory(inventory)

results_callback = ResultCallback()

play_src = dict(
	name = "show ip int brief",
	hosts = "csrs",
	gather_facts="no",
	connection="local",
	tasks=[
		dict(name="shoipintbrief", register="output", 
	             action=dict(module="ios_command", args=dict(commands="show ip int brief", provider=dict(host="{{ inventory_hostname }}", username="cisco", password="cisco",transport="cli"))))]
	)

play = Play().load(play_src, variable_manager=variable_manager, loader=loader)

tqm = None
try:
    tqm = TaskQueueManager(
            inventory=inventory,
            variable_manager=variable_manager,
            loader=loader,
            options=options,
            passwords=passwords,
            stdout_callback=results_callback,
        )
    result = tqm.run(play)
    print stdout_callback.hostresults
finally:
    if tqm is not None:
        tqm.cleanup()

#print result

		


