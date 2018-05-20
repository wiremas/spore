#include "spore.h"

#include <maya/MTypeId.h> 
#include <maya/MGlobal.h>

#include <maya/MSelectionList.h>
#include <maya/MPlugArray.h>

#include <maya/MItSelectionList.h>

#include <maya/MFnMesh.h>
#include <maya/MFnMeshData.h>
#include <maya/MFnArrayAttrsData.h>
#include <maya/MFnTypedAttribute.h>
#include <maya/MFnNumericAttribute.h>
#include <maya/MFnGenericAttribute.h>
#include <maya/MFnEnumAttribute.h>
#include <maya/MFnNumericData.h>
#include <maya/MFnIntArrayData.h>
#include <maya/MFnVectorArrayData.h>
#include <maya/MFnDoubleArrayData.h>
// #include <maya/MFnData.h>
// #include <maya/MFnVectorArrayData.h>
// #include <maya/MFnCompoundAttribute.h>
// #include <maya/MFnComponentListData.h>

#include <maya/MArrayDataHandle.h>
#include <maya/MArrayDataBuilder.h>
#include <maya/MDataHandle.h>

#include <maya/MPoint.h>
#include <maya/MPointArray.h>


MTypeId sporeLocator::id( 0x80028 );
// MString sporeLocator::drawRegistrantId( "sporeLocatorPlugin ");
// MString sporeLocator::drawDbClassification( "drawdb/geometry/sporeLocator ");

// input attributes
MObject sporeLocator::aInMesh;
// output attributes
MObject sporeLocator::aInstanceData;
// context attributes
MObject sporeLocator::aContextMode;
MObject sporeLocator::aBrushRadius;
MObject sporeLocator::aNumBrushSamples;
MObject sporeLocator::aFalloff;
MObject sporeLocator::aAlignSpace;
MObject sporeLocator::aMinDistance;
MObject sporeLocator::aStrength;
MObject sporeLocator::aMinRotation;
MObject sporeLocator::aMaxRotation;
MObject sporeLocator::aUniformScale;
MObject sporeLocator::aMinScale;
MObject sporeLocator::aMaxScale;
MObject sporeLocator::aScaleFactor;
MObject sporeLocator::aScaleAmount;
MObject sporeLocator::aMinOffset;
MObject sporeLocator::aMaxOffset;
// emit attributes
MObject sporeLocator::aEmitType;
MObject sporeLocator::aEmit;
MObject sporeLocator::aNumEmitSamples;
MObject sporeLocator::aMinRadius;
MObject sporeLocator::aEmitFromTexture;
MObject sporeLocator::aEmitTexture;
// dummy attributes
MObject sporeLocator::aGeoCached;
MObject sporeLocator::aPointsCached;
// storage attributes
MObject sporeLocator::aPosition;
MObject sporeLocator::aRotatio;
MObject sporeLocator::aScale;
MObject sporeLocator::aInstanceId;
MObject sporeLocator::aVisibility;
MObject sporeLocator::aNormal;
MObject sporeLocator::aTangent;
MObject sporeLocator::aUCoord;
MObject sporeLocator::aVCoord;
MObject sporeLocator::aPolyId;
MObject sporeLocator::aColor;
MObject sporeLocator::aIndex;

// sporeLocator::sporeLocator() {}
// sporeLocator::~sporeLocator() {}


void* sporeLocator::creator()
{
    return new sporeLocator();
}

MStatus sporeLocator::initialize()
{

    MStatus status = MS::kSuccess;

    // initialize function sets
    MFnEnumAttribute enumAttrFn;
    MFnTypedAttribute typedAttrFn;
    MFnNumericAttribute numericAttrFn;
    MFnGenericAttribute genericAttrFn;
    MFnIntArrayData intArrayAttrFn;
    MFnVectorArrayData vetcArrayAttrFn;
    MFnDoubleArrayData doubleArrayAttrFn;

    // input attribute
    aInMesh = typedAttrFn.create( "inMesh", "inMesh", MFnMeshData::kMesh, &status );
    typedAttrFn.setWritable( true );
    numericAttrFn.setHidden( false  );
    typedAttrFn.setReadable( true );
    typedAttrFn.setStorable( false );
    status = addAttribute( aInMesh );

    // output attributes
    aInstanceData = genericAttrFn.create( "instanceData", "instanceData", &status );
    status = genericAttrFn.addDataAccept( MFnArrayAttrsData::kDynArrayAttrs );
    genericAttrFn.setReadable( true );
    genericAttrFn.setWritable( true );
    genericAttrFn.setKeyable( false );
    status = addAttribute( aInstanceData );

    // context attributes
    aContextMode = enumAttrFn.create( "contextMode", "contextMode", 0, &status);
    enumAttrFn.addField( "Place", 0 );
    enumAttrFn.addField( "Spray", 1 );
    enumAttrFn.addField( "Scale", 2 );
    enumAttrFn.addField( "Align", 3 );
    enumAttrFn.addField( "Move", 4 );
    enumAttrFn.addField( "ID", 5 );
    enumAttrFn.addField( "Delete", 6 );
    enumAttrFn.setStorable( false );
    enumAttrFn.setKeyable( false );
    enumAttrFn.setConnectable( false );
    status = addAttribute( aContextMode );

    aBrushRadius = numericAttrFn.create( "brushRadius", "brushRadius", MFnNumericData::kDouble, 1, &status );
    numericAttrFn.setMin( 0.001 );
    numericAttrFn.setSoftMax( 10 );
    numericAttrFn.setConnectable( false );
    status = addAttribute( aBrushRadius );

    aNumBrushSamples = numericAttrFn.create( "numBrushSamples", "numBrushSamples", MFnNumericData::kInt, 0, &status );
    numericAttrFn.setMin( 1 );
    numericAttrFn.setSoftMax( 10 );
    numericAttrFn.setConnectable( false );
    status = addAttribute( aNumBrushSamples );

    aFalloff = enumAttrFn.create( "fallOff", "fallOff", 0, &status );
    enumAttrFn.addField( "None", 0 );
    enumAttrFn.addField( "Linear", 1 );
    enumAttrFn.setStorable( false );
    enumAttrFn.setKeyable( false );
    enumAttrFn.setConnectable( false );
    status = addAttribute( aFalloff );

    aMinDistance = numericAttrFn.create( "minDistance", "minDistance", MFnNumericData::kDouble, 0.1, &status );
    numericAttrFn.setMin( 0.001 );
    numericAttrFn.setSoftMax( 10 );
    numericAttrFn.setConnectable( false );
    status = addAttribute( aMinDistance );

    aAlignSpace = enumAttrFn.create( "alignTo", "alignTo", 0, &status );
    enumAttrFn.addField( "Normal", 0 );
    enumAttrFn.addField( "World", 1 );
    enumAttrFn.addField( "Object", 2 );
    enumAttrFn.addField( "Stroke", 3 );
    enumAttrFn.setStorable( false );
    enumAttrFn.setKeyable( false );
    enumAttrFn.setConnectable( false );
    status = addAttribute( aAlignSpace );

    aStrength = numericAttrFn.create( "strength", "strength", MFnNumericData::kDouble, 0.1, &status );
    numericAttrFn.setMin( 0.001 );
    numericAttrFn.setSoftMax( 10 );
    numericAttrFn.setConnectable( false );
    status = addAttribute( aStrength );

    aMinRotation = numericAttrFn.createPoint( "minRotation", "minRotation" );
    numericAttrFn.setMin( -360, -360, -360 );
    numericAttrFn.setMax( 360, 360, 360 );
    numericAttrFn.setDefault( -3.0, -180.0, -3.0 );
    numericAttrFn.setConnectable( false );
    status = addAttribute( aMinRotation );

    aMaxRotation = numericAttrFn.createPoint( "maxRotation", "maxRotation" );
    numericAttrFn.setMin( -360, -360, -360 );
    numericAttrFn.setMax( 360, 360, 360 );
    numericAttrFn.setDefault( 3.0, 180.0, 3.0 );
    numericAttrFn.setConnectable( false );
    status = addAttribute( aMaxRotation );

    aUniformScale = numericAttrFn.create( "uniformScale", "uniformScale", MFnNumericData::kBoolean, 1.1, &status );
    numericAttrFn.setConnectable( false );
    status = addAttribute( aUniformScale );

    aMinScale = numericAttrFn.createPoint( "minScale", "minScale" );
    numericAttrFn.setDefault( 0.9, 0.9, 0.9 );
    numericAttrFn.setConnectable( false );
    status = addAttribute( aMinScale );

    aMaxScale = numericAttrFn.createPoint( "maxScale", "maxScale" );
    numericAttrFn.setDefault( 1.1, 1.1, 1.1 );
    numericAttrFn.setConnectable( false );
    status = addAttribute( aMaxScale );

    aScaleFactor = numericAttrFn.create( "scaleFactor", "scaleFactor", MFnNumericData::kDouble, 1.05, &status );
    numericAttrFn.setMin( 0.001 );
    numericAttrFn.setSoftMin( 0.8 );
    numericAttrFn.setSoftMax( 1.2 );
    numericAttrFn.setConnectable( false );
    status = addAttribute( aScaleFactor );

    aScaleAmount = numericAttrFn.create( "scaleAmount", "scaleAmount", MFnNumericData::kDouble, 0.1, &status );
    numericAttrFn.setMin( 0.001 );
    numericAttrFn.setSoftMax( 10 );
    numericAttrFn.setConnectable( false );
    status = addAttribute( aScaleAmount );

    aMinOffset = numericAttrFn.create( "minOffset", "minOffset", MFnNumericData::kDouble, 0, &status );
    numericAttrFn.setMin( -10 );
    numericAttrFn.setSoftMax( 10 );
    numericAttrFn.setConnectable( false );
    status = addAttribute( aMinOffset );

    aMaxOffset = numericAttrFn.create( "maxOffset", "maxOffset", MFnNumericData::kDouble, 0, &status );
    numericAttrFn.setSoftMin( -10 );
    numericAttrFn.setSoftMax( 10 );
    numericAttrFn.setConnectable( false );
    status = addAttribute( aMaxOffset );

    // emit attributes
    aEmitType = enumAttrFn.create( "emitType", "emitType", 0, &status );
    enumAttrFn.addField( "Random", 0 );
    enumAttrFn.addField( "Jitter Grid", 1 );
    enumAttrFn.addField( "Poisson", 2 );
    enumAttrFn.setStorable( false );
    enumAttrFn.setKeyable( false );
    enumAttrFn.setConnectable( false );
    status = addAttribute( aEmitType );

    aEmit = numericAttrFn.create( "emit", "emit", MFnNumericData::kBoolean, 0 &status);
    // numericAttrFn.setReadable( true );
    // numericAttrFn.setWritable( true );
    // numericAttrFn.setKeyable( false  );
    numericAttrFn.setHidden( false  );
    status = addAttribute( aEmit );

    // node addributes
    aNumEmitSamples = numericAttrFn.create( "numSamples", "numSamples", MFnNumericData::kInt, 0, &status );
    status = addAttribute( aNumEmitSamples );

    aMinRadius = numericAttrFn.create( "minRadius", "minRadius", MFnNumericData::kInt, 0, &status );
    status = addAttribute( aMinRadius );

    aEmitFromTexture = numericAttrFn.createColor( "emitFromTexture", "emitFromTexture" );
    status = addAttribute( aEmitFromTexture );
    //
    // aNumInstances = numericAttrFn.create( "numInstances", "numInstances", MFnNumericData::kInt, 0, &status );
    // numericAttrFn.setDefault( 1 );
    // numericAttrFn.setMin( 1 );
    // status = addAttribute( aNumInstances );
    //
    // aPointVisibility = numericAttrFn.create( "pointVisibility", "pointVisibility", MFnNumericData::kBoolean, 0, &status );
    // numericAttrFn.setDefault( true );
    // status = addAttribute( aPointVisibility );
    //
    // aDisplaySize = numericAttrFn.create( "displaySize", "displaySize", MFnNumericData::kDouble, 0, &status );
    // numericAttrFn.setDefault( 2.0 );
    // numericAttrFn.setMin( 1.0 );
    // status = addAttribute( aDisplaySize );
    //
    // aBrushRadius = numericAttrFn.create( "brushRadius", "brushRadiu", MFnNumericData::kDouble, 0, &status );
    // numericAttrFn.setDefault( 2.0 );
    // numericAttrFn.setMin( 1.0 );
    // status = addAttribute( aBrushRadius );
    //
    //
    // status = attributeAffects(aEmitRequest, instanceData);

    CHECK_MSTATUS( status );
	return( status );
}
/*
void sporeLocator::draw( M3dView & view, const MDagPath & path,
                             M3dView::DisplayStyle style,
                             M3dView::DisplayStatus status )
{
    // MStatus status;
    MObject thisNode = thisMObject();

    // get position data
    MPlug instDataPlug ( thisNode, instanceData );
    MObject instDataAttr;
    instDataPlug.getValue( instDataAttr );
    MFnArrayAttrsData arrayAttrsFn(instDataAttr);
    MVectorArray position = arrayAttrsFn.getVectorData( "position" );

    // get point display size attr
    MPlug displaySizePlug ( thisNode, aDisplaySize );
    float pointSize;
    displaySizePlug.getValue( pointSize );

    // get point visibility
    MPlug displayVisibilityPlug ( thisNode, aPointVisibility );
    bool pointVisibility;
    displayVisibilityPlug.getValue( pointVisibility );

    // std::cout << pointVisibility << std::endl;

    if ( pointVisibility == 1 )
    {

        view.beginGL();

        glPushAttrib( GL_CURRENT_BIT );

        if ( status == M3dView::kActive )
            view.setDrawColor( 13, M3dView::kActiveColors );
        else
            view.setDrawColor( 13, M3dView::kDormantColors );

        glPointSize( pointSize );
        glBegin( GL_POINTS );

        for ( int i = 0; i < position.length(); i++ )
        {
            glVertex3f( position[i].x, position[i].y, position[i].z );
        }

        glEnd();

        view.endGL();
    }
}
*/
// bool sporeLocator::isBounded() const
// {
//     return false;
// }
//
// MBoundingBox sporeLocator::boundingBox() const
// {
//     return MBoundingBox();
// }


MStatus sporeLocator::compute( const MPlug& plug, MDataBlock& data )
{
    // MStatus status;
    MGlobal::displayInfo("FOO");
    MStatus status;

    /*
    if ( plug == instanceData )
        MGlobal::displayInfo("BAR");

        MDataHandle inMeshData = data.inputValue( aInMesh, &status );
        MFnMesh meshFn( inMeshData.asMesh(), &status );
        // MFnMeshPolygon polyFn(inMeshData.asMesh(), &status );
        // MGlobal::displayInfo( inMeshData.asMesh() );
        MDataHandle inNumSamples = data.inputValue( aNumSamples, &status );
        int numSamples = inNumSamples.asInt();
        MDataHandle inNumInstances = data.inputValue( aNumInstances, &status );
        int numInstances = inNumInstances.asInt();

        MDataHandle outputData = data.outputValue( plug );
        bool t = true;
        bool f = false;

        MObject genericAttr;
        MObject attrsArrayObj;
        MFnArrayAttrsData arrayAttrsDataFn;

        if ( outputData.isGeneric( t, f ) )


            attrsArrayObj = arrayAttrsDataFn.create( &status );
            MVectorArray outPos = arrayAttrsDataFn.vectorArray( "position", &status );


            // genericAttr = genericAttrFn.create( &status ); // vectorArray("position", &status);
            // points = genericAttr.vectorArray("position", &status );

            for ( int i = 0; i < numSamples ; i++ )
            {
                double zero = 0.0;
                MPoint pnt(zero, i, zero);
                outPos.append(pnt);
            }

            outputData.set( attrsArrayObj );

    // int index = plug.logicalIndex( &status );
    // MArrayDataHandle hOutArray = data.outputArrayValue(instanceData, &status );
    // MArrayDataBuilder bOutArray = hOutArray.builder( &status );
    // MDataHandle hOut = bOutArray.addElement(index, &status );
    */
    return( MS::kSuccess );
}


//
// DrawOverride
//

/*
ptcDrawOverride::ptcDrawOverride( const MObject& obj  )
: MHWRender::MPxDrawOverride( obj, ptcDrawOverride::draw )
{
    std::cout << "constructor" << std::endl;
}

ptcDrawOverride::~ptcDrawOverride()
{
}

MHWRender::DrawAPI ptcDrawOverride::supportedDrawAPIs() const
{
    return( MHWRender::kOpenGL | MHWRender::kDirectX11 | MHWRender::kOpenGLCoreProfile );
}

MUserData* ptcDrawOverride::prepareForDraw(
	const MDagPath& objPath,
	const MDagPath& cameraPath,
	const MHWRender::MFrameContext& frameContext,
	MUserData* oldData)
{
	ptcData* data = dynamic_cast<ptcData*>(oldData);
	if (!data)
	{
		data = new ptcData();
	}
    return( NULL );
}


void ptcDrawOverride::draw(const MHWRender::MDrawContext& context, const MUserData* data)
{
    cout << "I'M DRAWING NOW!!";
}
*/


MStatus initializePlugin( MObject obj )
{ 
	MStatus   status;
	MFnPlugin plugin( obj, "Anno Schachner", "0.1", "Any");

	status = plugin.registerNode ( "sporeLocator",
                                    sporeLocator::id,
                                    &sporeLocator::creator,
                                    &sporeLocator::initialize,
                                    MPxNode::kLocatorNode);
                                    // &sporeLocator::drawDbClassification );

	if (!status)
    {
		status.perror("registerNode");
		return( status );
	}

    // status = MHWRender::MDrawRegistry::registerDrawOverrideCreator(
    //                                 sporeLocator::drawDbClassification,
    //                                 sporeLocator::drawRegistrantId,
    //                                 ptcDrawOverride::Creator );

	// if (!status)
    // {
	//     status.perror("registerNode");
	//     return( status );
	// }

	return( status );
}

MStatus uninitializePlugin( MObject obj)
{
	MStatus   status;
	MFnPlugin plugin( obj );

    // status = MHWRender::MDrawRegistry::deregisterDrawOverrideCreator(
    //                                 sporeLocator::drawDbClassification,
    //                                 sporeLocator::drawRegistrantId );

	// if (!status)
    // {
	//     status.perror("deregisterNode");
	//     return( status );
	// }
    //

    status = plugin.deregisterNode( sporeLocator::id );

	if (!status)
    {
		status.perror( "deregisterNode" );
		return( status );
	}
	return( status );
}



