import ghidra.app.script.GhidraScript;
import ghidra.program.model.listing.*;
import java.io.*;

/**
 * DumpSyms.java -- function + symbol census for one Ghidra program.
 *
 * The export path arrives as the FIRST script argument, which is the mechanism
 * Ghidra guarantees across the launcher boundary. (An environment variable set
 * in the calling .bat did NOT reach this process in testing, and `setlocal`
 * scopes it away entirely -- both recorded in C-00.)
 *
 * Invoke as:
 *   analyzeHeadless <projDir> <projName> -import <target> ^
 *       -scriptPath <dir> -postScript DumpSyms.java <out.tsv>
 *
 * Verified against Ghidra 12.1.4 headless, round 23.
 */
public class DumpSyms extends GhidraScript {

    public void run() throws Exception {
        String[] args = getScriptArgs();
        if (args.length < 1 || args[0] == null || args[0].isEmpty()) {
            println("EXPORT_FAILED=no_arg");
            throw new RuntimeException("DumpSyms requires <out.tsv> as script arg 1");
        }
        File outFile = new File(args[0]);
        File parent = outFile.getParentFile();
        if (parent != null && !parent.exists()) parent.mkdirs();

        PrintWriter w = new PrintWriter(new OutputStreamWriter(
                new FileOutputStream(outFile), "UTF-8"));

        w.println("# program\t" + currentProgram.getName());
        w.println("# language\t" + currentProgram.getLanguageID());
        w.println("# compiler\t" + currentProgram.getCompilerSpec().getCompilerSpecID());
        w.println("# imageBase\t" + currentProgram.getImageBase());
        w.println("# kind\taddress\tname\tsize\tnamespace\tis_thunk");

        FunctionManager fm = currentProgram.getFunctionManager();
        int total = 0, named = 0, thunks = 0;
        long bodyBytes = 0;

        for (Function f : fm.getFunctions(true)) {
            String nm = f.getName();
            boolean isNamed = !(nm.startsWith("FUN_") || nm.startsWith("thunk_FUN_"));
            String ns = f.getParentNamespace() != null
                    ? f.getParentNamespace().getName() : "";
            boolean th = f.isThunk();
            long sz = f.getBody().getNumAddresses();
            w.println("FUNC\t" + f.getEntryPoint() + "\t" + nm + "\t" + sz
                    + "\t" + ns + "\t" + th);
            if (isNamed) named++;
            if (th) thunks++;
            bodyBytes += sz;
            total++;
        }
        w.println("# SUMMARY\ttotal=" + total + "\tnamed=" + named
                + "\tthunks=" + thunks + "\tbodybytes=" + bodyBytes);
        w.close();

        println("EXPORTED_FUNCTIONS=" + total);
        println("NAMED_FUNCTIONS=" + named);
        println("THUNKS=" + thunks);
        println("TOTAL_BODY_BYTES=" + bodyBytes);
    }
}
