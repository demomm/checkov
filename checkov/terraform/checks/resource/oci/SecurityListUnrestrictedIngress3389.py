from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class SecurityListUnrestrictedIngress3389(BaseResourceCheck):
    def __init__(self):
        name = "Ensure VCN inbound security lists allow all traffic on 3389 port."
        id = "CKV_OCI_20"
        supported_resources = ['oci_core_security_list']
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        if 'ingress_security_rules' in conf:
            self.evaluated_keys = ['ingress_security_rules']
            rules = conf.get("ingress_security_rules")
            for idx, rule in enumerate(rules):
                if not "0.0.0.0/0" in rule['source'][0]:
                    self.evaluated_keys = [f'ingress_security_rules/[0]/[{idx}]/source']
                    return CheckResult.SKIPPED

                if not ((rule['protocol'][0] != '1' and (not 'udp_options' in rule) and (not 'tcp_options' in rule))
                        or (self.scan_protocol_conf(rule, 'tcp_options', idx) != CheckResult.FAILED
                            and self.scan_protocol_conf(rule, 'udp_options', idx) != CheckResult.FAILED)
                        or rule['protocol'][0] == 'all'):
                    self.evaluated_keys = [f'ingress_security_rules/[0]/[{idx}]']
                    return CheckResult.FAILED

            return CheckResult.PASSED

        return CheckResult.SKIPPED

    def scan_protocol_conf(self, rule, protocol_name, idx):
        """ scan udp/tcp_options configuration"""
        if protocol_name in rule:
            max_port = rule[protocol_name][0]['max'][0]
            min_port = rule[protocol_name][0]['min'][0]
            if min_port <= 3389 and max_port >= 3389:
                return CheckResult.SKIPPED
        self.evaluated_keys = [f'ingress_security_rules/[0]/[{idx}]/protocol/[0]/{protocol_name}']
        return CheckResult.FAILED


check = SecurityListUnrestrictedIngress3389()
