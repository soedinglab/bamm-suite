from collections import OrderedDict
import io
import subprocess

class CommandlineModule:
    def __init__(self, command_name, config):
        cmd_flag_templates = OrderedDict()
        options = OrderedDict()
        for option_name, flag_template in config:
            options[option_name] = None
            cmd_flag_templates[option_name] = flag_template

        self._command_name = command_name
        self._cmd_flag_templates = cmd_flag_templates
        self._options = options
        self._initialized = True

    def __setattr__(self, name, value):
        if not '_initialized' in self.__dict__:
            super().__setattr__(name, value)
        elif name in self._options:
            self._options[name] = value
        else:
            raise OptionError('unknown option %r' % name)

    def __getattr__(self, name):
        if not '_initialized' in self.__dict__:
            return  super().__getattr__(name)
        elif name in self._options:
            return self._options[name]
        elif name in self.__dict__:
            return  super().__getattr__(name)
        else:
            raise OptionError('unknown option %r' % name)

    @property
    def command_tokens(self):
        # TODO does not support positional arguments yet.
        cmd_tokens = [self._command_name]
        for option_name, option_value in self._options.items():
            if option_value is None:
                continue
            flag_tmpl = self._cmd_flag_templates[option_name]
            cmd_tokens.append(flag_tmpl)
            if isinstance(option_value, str):
                cmd_tokens.append('%r' % option_value)
            elif isinstance(option_value, bool):
                if option_value:
                    cmd_tokens.append('%s' % flag_tmpl)
            elif isinstance(option_value, list):
                for item in option_value:
                    if isinstance(item, str):
                        cmd_tokens.append('%r' % item)
                    else:
                        cmd_tokens.append(str(item))
            else:
                cmd_tokens.append(str(option_value))
        return cmd_tokens


    def run(self, **kw_args):
        extra_args = {
            'universal_newlines': True
        }
        extra_args.update(kw_args)
        return subprocess.run(self.command_tokens, **extra_args)

class OptionError(ValueError):
    pass

class ShootPengModule(CommandlineModule):
    def __init__(self):
        config = [
            ('fasta_file', None),
            ('meme_output', '-o'),
            ('json_output', '-j'),
            ('temp_dir', '-d'),
            ('bg_sequences', '--background-sequences'),
            ('pattern_length', '-w'),
            ('zscore_threshold', '-t'),
            ('count_threshold', '--count-threshold'),
            ('bg_model_order', '--bg-model-order'),
            ('strand', '--strand'),
            ('objective_function', '--iupac_optimization_score'),
            ('enrich_pseudocount_factor', '--enrich_pseudocount_factor'),
            ('no_em', '--no-em'),
            ('em_saturation_threshold', '-a'),
            ('em_threshold', '--em-threshold'),
            ('em_max_iterations', '--em-max-iterations'),
            ('no_merging', '--no-merging'),
            ('bit_factor_threshold', '-b'),
            ('use_default_pwm', '--use-default-pwm'),
            ('pwm_pseudo_counts', '--pseudo-counts'),
            ('n_threads', '--threads'),
            ('silent', '--silent'),
            super().__init__('shoot_peng.py', config)
]




