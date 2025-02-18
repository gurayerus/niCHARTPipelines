import os
import re
from pathlib import Path

from nipype.interfaces.base import (BaseInterface, BaseInterfaceInputSpec,
                                    Directory, File, TraitedSpec, traits)

from niCHARTPipelines import ROIRelabeler as relabeler

###---------Interface------------
def get_basename(in_file, suffix_to_remove, ext_to_remove = ['.nii.gz', '.nii']):
    '''Get file basename 
    - Extracts the base name from the input file
    - Removes a given suffix + file extension
    '''
    ## Get file basename
    out_str = os.path.basename(in_file)

    ## Remove suffix and extension
    for tmp_ext in ext_to_remove:
        out_str, num_repl = re.subn(suffix_to_remove + tmp_ext + '$', '', out_str)
        if num_repl > 0:
            break

    ## Return basename
    if num_repl == 0:
        return None
    return out_str

class ROIRelabelInputSpec(BaseInterfaceInputSpec):
    map_csv_file = File(exists=True, mandatory=True, desc='the map csv file')
    in_dir = Directory(mandatory=True, desc='the input dir')
    in_suff = traits.Str(mandatory=False, desc='the input image suffix')    
    out_dir = Directory(mandatory=True, desc='the output dir') 
    out_suff = traits.Str(mandatory=False, desc='the output image suffix')    

class ROIRelabelOutputSpec(TraitedSpec):
    out_dir = File(desc='the output image')

class ROIRelabel(BaseInterface):
    input_spec = ROIRelabelInputSpec
    output_spec = ROIRelabelOutputSpec

    def _run_interface(self, runtime):

        ## Constant params
        label_from = 'IndexConsecutive'     # Column header in mapping file
        label_to = 'IndexMUSE'              # Column header in mapping file
        img_ext_type = '.nii.gz'

        # Set input args
        if not self.inputs.in_suff:
            self.inputs.in_suff = ''

        if not self.inputs.out_suff:
            self.inputs.out_suff = '_relabeled'
        
        ## Create output folder
        if not os.path.exists(self.inputs.out_dir):
            os.makedirs(self.inputs.out_dir)
        
        infiles = Path(self.inputs.in_dir).glob('*' + self.inputs.in_suff + img_ext_type)
        for in_img_name in infiles:
            ## Get args
            in_bname = get_basename(in_img_name, self.inputs.in_suff, [img_ext_type])
            out_img_name = os.path.join(self.inputs.out_dir,
                                        in_bname + self.inputs.out_suff + img_ext_type)

            ## Call the main function
            relabeler.relabel_roi_img(in_img_name,
                                      self.inputs.map_csv_file,
                                      label_from,
                                      label_to,
                                      out_img_name)
            
        # And we are done
        return runtime

    def _list_outputs(self):
        return {'out_dir': self.inputs.out_dir}
