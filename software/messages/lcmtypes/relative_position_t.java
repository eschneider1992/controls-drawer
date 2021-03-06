/* LCM type definition class file
 * This file was automatically generated by lcm-gen
 * DO NOT MODIFY BY HAND!!!!
 */

package lcmtypes;
 
import java.io.*;
import java.util.*;
import lcm.lcm.*;
 
public final class relative_position_t implements lcm.lcm.LCMEncodable
{
    public long utime;
    public double velocity;
    public double position[];
 
    public relative_position_t()
    {
        position = new double[2];
    }
 
    public static final long LCM_FINGERPRINT;
    public static final long LCM_FINGERPRINT_BASE = 0xbceca6b30e5916ebL;
 
    static {
        LCM_FINGERPRINT = _hashRecursive(new ArrayList<Class<?>>());
    }
 
    public static long _hashRecursive(ArrayList<Class<?>> classes)
    {
        if (classes.contains(lcmtypes.relative_position_t.class))
            return 0L;
 
        classes.add(lcmtypes.relative_position_t.class);
        long hash = LCM_FINGERPRINT_BASE
            ;
        classes.remove(classes.size() - 1);
        return (hash<<1) + ((hash>>63)&1);
    }
 
    public void encode(DataOutput outs) throws IOException
    {
        outs.writeLong(LCM_FINGERPRINT);
        _encodeRecursive(outs);
    }
 
    public void _encodeRecursive(DataOutput outs) throws IOException
    {
        outs.writeLong(this.utime); 
 
        outs.writeDouble(this.velocity); 
 
        for (int a = 0; a < 2; a++) {
            outs.writeDouble(this.position[a]); 
        }
 
    }
 
    public relative_position_t(byte[] data) throws IOException
    {
        this(new LCMDataInputStream(data));
    }
 
    public relative_position_t(DataInput ins) throws IOException
    {
        if (ins.readLong() != LCM_FINGERPRINT)
            throw new IOException("LCM Decode error: bad fingerprint");
 
        _decodeRecursive(ins);
    }
 
    public static lcmtypes.relative_position_t _decodeRecursiveFactory(DataInput ins) throws IOException
    {
        lcmtypes.relative_position_t o = new lcmtypes.relative_position_t();
        o._decodeRecursive(ins);
        return o;
    }
 
    public void _decodeRecursive(DataInput ins) throws IOException
    {
        this.utime = ins.readLong();
 
        this.velocity = ins.readDouble();
 
        this.position = new double[(int) 2];
        for (int a = 0; a < 2; a++) {
            this.position[a] = ins.readDouble();
        }
 
    }
 
    public lcmtypes.relative_position_t copy()
    {
        lcmtypes.relative_position_t outobj = new lcmtypes.relative_position_t();
        outobj.utime = this.utime;
 
        outobj.velocity = this.velocity;
 
        outobj.position = new double[(int) 2];
        System.arraycopy(this.position, 0, outobj.position, 0, 2); 
        return outobj;
    }
 
}

