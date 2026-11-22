import java.nio.file.Files
import java.nio.file.Paths

def source = props.getProperty('accounts.source')
if (source == null) {
    // GUI reads the same resolved account file as the native CSV Data Set.
    source = vars.get('account_source')
}
def lines = Files.readAllLines(Paths.get(source))
int row = lines.indexOf(vars.get('cookie'))
vars.put('account_no', row > 0 ? row.toString() : 'unknown')
vars.put('trial_phase', props.getProperty('trial.phase', 'full'))
def tokens = props.getProperty('ctokens.file')
if (tokens && row > 0) {
    vars.put('account_ctoken', java.net.URLEncoder.encode(Files.readAllLines(Paths.get(tokens))[row], 'UTF-8').replace('+', '%20'))
}
